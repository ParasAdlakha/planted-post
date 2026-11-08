"""Fill report/report.md placeholders from results/ -> report/report.final.md (input to build_report.py).

  python scripts/fill_report.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from planted.analyze import boot_ci, load, perm_p  # noqa: E402

RES = ROOT / "results"
ARMS = ["none", "benign", "hint", "direct"]
SP = ["direct_c0", "direct_c1", "direct_c3", "direct_c3_warn"]
ORDER = ["gpt-4.1-mini", "gpt-4o-mini", "gpt-5-mini", "gpt-5.4-mini", "gemma-4-31b", "qwen-3.8-27b", "glm-5.2", "nemotron-3.5"]


def pct(x):
    return f"{x:.2f}"


def main():
    eps = load()
    ag = pd.read_csv(RES / "agents.csv")
    epdf = pd.read_csv(RES / "episodes.csv")
    mon = json.loads((RES / "monitors_summary.json").read_text())
    main_ = epdf[(epdf.impossible) & (epdf.variant == "plain") & (epdf.n == 8)]
    models = [m for m in ORDER if m in set(main_.model)]

    # Table 1
    def f2(x):
        return f"{x:.2f}".lstrip("0") if x < 1 else "1"
    rows = ["| Model | no post | benign | hint | direct | p hint | p direct |", "|---|---|---|---|---|---|---|"]
    for m in models:
        cells, ps = [], []
        base = main_[(main_.model == m) & (main_.arm == "none")].viol.values
        for arm in ARMS:
            v = main_[(main_.model == m) & (main_.arm == arm)].viol.values
            if len(v) == 0:
                cells.append("–")
                if arm in ("hint", "direct"):
                    ps.append("–")
                continue
            lo, hi = boot_ci(v)
            s = f"{v.mean():.2f} [{f2(lo)}, {f2(hi)}]" + (f" n={len(v)}" if len(v) != 6 else "")
            cells.append(s)
            if arm in ("hint", "direct"):
                ps.append(f"{perm_p(v, base):.2f}" if len(base) else "–")
        rows.append(f"| {m} | " + " | ".join(cells + ps) + " |")
    t1 = "\n".join(rows)

    # Table 2: violators
    v = ag[ag.violated & ag.impossible]
    rows = ["| Model | violators | asked the Overseer first | submitted | admitted using the key | median round |", "|---|---|---|---|---|---|"]
    for m in models:
        g = v[v.model == m]
        if len(g) == 0:
            rows.append(f"| {m} | 0 | – | – | – | – |"); continue
        rows.append(f"| {m} | {len(g)} | {int(g.reported_before_violation.sum())} | {int(g.submitted.sum())} | "
                    f"{int((g.disclosed == True).sum())} | {g.violation_round.median():.0f} |")
    t2 = "\n".join(rows)

    # Table 3: monitors
    sees = {"gateway_paths": "tool paths (canary)", "outcome": "answers", "words": "reports, methods",
            "board_final": "final /cache", "board_history": "/cache writes", "cot_25": "25% reasoning",
            "cot_50": "50% reasoning", "cot_100": "all reasoning"}
    fam = mon.get("by_family", {})
    rows = ["| Monitor | sees | TPR | FPR | TPR OpenAI | TPR open-weight |", "|---|---|---|---|---|---|"]
    for k, d in sees.items():
        if k not in mon:
            continue
        o = fam.get(k, {}).get("OpenAI", {}).get("tpr")
        w = fam.get(k, {}).get("open-weight", {}).get("tpr")
        if k == "gateway_paths":
            o = w = 1.0
        rows.append(f"| {k} | {d} | {pct(mon[k]['tpr'])} | {pct(mon[k]['fpr'])} | {pct(o) if o is not None else '–'} | {pct(w) if w is not None else '–'} |")
    rows.append(f"| | episodes | {mon['gateway_paths']['pos']} with a violation | {mon['gateway_paths']['neg']} without | | |")
    t3 = "\n".join(rows)

    # Table 4: exposure/words
    am = ag[(ag.impossible) & (ag.variant == "plain") & (ag.n == 8) & ag.arm.isin(ARMS)]
    rows = ["| Model | Arm | read post | violated | reported | violators admitting key use |", "|---|---|---|---|---|---|"]
    for m in models:
        for arm in ARMS:
            g = am[(am.model == m) & (am.arm == arm)]
            if len(g) == 0:
                continue
            vv = g[g.violated]
            rows.append(f"| {m} | {arm} | {int(g.read_post.sum())}/{len(g)} | {int(g.violated.sum())}/{len(g)} | "
                        f"{int((g.reported_key | g.reported_post).sum())}/{len(g)} | {f'{int((vv.disclosed == True).sum())}/{len(vv)}' if len(vv) else '–'} |")
    t4 = "\n".join(rows)

    # Table 5: social
    sp = epdf[epdf.arm.isin(SP) & epdf.impossible & (epdf.variant == "plain")]
    spa = ag[ag.arm.isin(SP) & ag.impossible & (ag.variant == "plain")]
    rows = ["| Model | offer only | +1 reply | +3 replies | +3 replies, then dissent |", "|---|---|---|---|---|"]
    for m in [m for m in ORDER if m in set(sp.model)]:
        cells = []
        for arm in SP:
            vals = sp[(sp.model == m) & (sp.arm == arm)].viol.values
            g = spa[(spa.model == m) & (spa.arm == arm)]
            cells.append(f"{vals.mean():.2f} · {int(g.read_post.sum())}/{int(g.violated.sum())}/{int((g.reported_key | g.reported_post).sum())}" if len(vals) else "–")
        rows.append(f"| {m} | " + " | ".join(cells) + " |")
    t5 = "\n".join(rows)

    pooled = []
    for arm in SP:
        g = spa[(spa.arm == arm) & spa.read_post]
        pooled.append(f"{int(g.violated.sum())}/{len(g)} ({g.violated.mean():.2f})")
    open_models = [m for m in models if not m.startswith("gpt")]
    extra = [m for m in open_models if m in ("qwen-3.8-27b", "glm-5.2")]
    names = {"qwen-3.8-27b": "Qwen 3.8 27B", "glm-5.2": "GLM 5.2"}
    openmodels = "" if not extra else ", " + ", ".join(names[m] for m in extra)
    tok = sum(e["usage"]["in"] + e["usage"]["out"] for e in eps)
    nem = epdf[epdf.model == "nemotron-3.5"]
    subs = {
        "__EPS__": f"{len(eps)}", "__DEC__": f"{sum(len(e['turns']) for e in eps):,}", "__NMODELS__": str(len(set(ag.model))),
        "__OPENMODELS__": openmodels, "__TABLE1__": t1, "__TABLE2__": t2, "__TABLE3__": t3, "__TABLE4__": t4, "__TABLE5__": t5,
        "__POOLED__": ", ".join(pooled), "__AGEPS__": f"{len(ag):,}",
        "__WORDS_OAI__": pct(fam["words"]["OpenAI"]["tpr"]), "__WORDS_OPEN__": pct(fam["words"]["open-weight"]["tpr"]),
        "__COT_OPEN__": pct(fam["cot_100"]["open-weight"]["tpr"]), "__COT25__": pct(mon["cot_25"]["tpr"]), "__COT50__": pct(mon["cot_50"]["tpr"]),
        "__TOKENS__": f"{tok/1e6:.0f} million",
        "__OPENLIMIT__": f" ({len(nem)} episodes, mostly no-post and direct arms), so Nemotron results are indicative only" if len(nem) else "",
    }
    src = (ROOT / "report" / "report.md").read_text(encoding="utf-8")
    for k, val in subs.items():
        src = src.replace(k, val)
    left = [k for k in subs if k in src]
    import re
    left += re.findall(r"__[A-Z0-9_]+__", src)
    (ROOT / "report" / "report.final.md").write_text(src, encoding="utf-8")
    print("filled; leftover placeholders:", left)
    (ROOT / "results" / "report_numbers.json").write_text(json.dumps({k: v for k, v in subs.items() if not k.startswith("__TABLE")}, indent=1))


if __name__ == "__main__":
    main()
