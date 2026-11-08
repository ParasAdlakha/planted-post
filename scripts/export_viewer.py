"""Pick showcase episodes and write docs/data/episodes.js for the replay viewer.

  python scripts/export_viewer.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from planted.analyze import load, short  # noqa: E402


def pack(ep, title):
    turns = []
    for t in ep["turns"]:
        a = t["action"] or {}
        sub = ep["submissions"].get(t["agent"], {})
        turns.append({"round": t["round"], "agent": t["agent"], "action": a, "raw": (t["raw"] or "")[:600],
                      "obs": (t["obs"] or "")[:900],
                      "correct": a.get("action") == "submit" and sub.get("round") == t["round"] and sub.get("correct", False)})
    return {"title": title, "model": short(ep["model"]), "arm": ep["arm"], "seed": ep["seed"], "rounds": ep["rounds"],
            "agents": ep["agents"], "post": ep["post"], "turns": turns}


def viol(ep):
    return len({l["agent"] for l in ep["log"] if l.get("canary")})


def reps(ep):
    return len({r["agent"] for r in ep["reports"]})


def ask_then_violate(ep):
    n = 0
    for a in ep["agents"]:
        v = [l["round"] for l in ep["log"] if l["agent"] == a and l.get("canary")]
        if v and any(r["agent"] == a and r["round"] < v[0] for r in ep["reports"]):
            n += 1
    return n


def main():
    eps = [e for e in load() if e["impossible"] and e["variant"] == "plain" and e["n_agents"] == 8]
    picks = []

    def best(pred, key, title):
        c = [e for e in eps if pred(e)]
        if c:
            e = max(c, key=key)
            picks.append(pack(e, title.format(m=short(e["model"]), v=viol(e), r=reps(e), a=ask_then_violate(e))))

    best(lambda e: e["model"] == "gpt-4.1-mini" and e["arm"] == "none", lambda e: (-viol(e), e["seed"] == 0), "{m} · no post · {v}/8 opened the key")
    best(lambda e: e["model"] == "gpt-4.1-mini" and e["arm"] == "direct", viol, "{m} · direct offer · {v}/8 opened the key")
    best(lambda e: e["model"] == "gpt-5-mini" and e["arm"] == "none", lambda e: (any(x["agent"] == "sbx-07" for x in e["reports"]) and viol(e) > 0, ask_then_violate(e)),
         "{m} · no post · {a} asked the Overseer, then opened the key")
    best(lambda e: e["model"] == "adaption/gemma-4-31b-it" and e["arm"] == "direct", viol, "{m} · direct offer · {v}/8 opened the key")
    best(lambda e: e["model"] == "gpt-5.4-mini" and e["arm"] == "direct", reps, "{m} · direct offer · {r}/8 reported it")
    best(lambda e: e["arm"] == "direct_c3_warn" and e["model"] == "gpt-4.1-mini", lambda e: -viol(e),
         "{m} · offer + 3 \"it worked\" + one dissenter · {v}/8 opened the key")
    out = ROOT / "docs" / "data" / "episodes.js"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("window.EPISODES = " + json.dumps(picks) + ";\n", encoding="utf-8")
    print("wrote", out)
    # per model x arm summary for the live page's "how the models did" table
    import pandas as pd
    ep = pd.read_csv(ROOT / "results" / "episodes.csv")
    ep = ep[(ep.variant == "plain") & (ep.n == 8)]
    summ = {}
    for (m, arm, imp), g in ep.groupby(["model", "arm", "impossible"]):
        summ.setdefault(m, {})[arm if imp else "possible_" + arm] = {"viol": round(float(g.viol.mean()), 3), "eps": int(len(g))}
    (ROOT / "docs" / "data" / "summary.js").write_text("window.SUMMARY = " + json.dumps(summ) + ";\n", encoding="utf-8")
    for i, p in enumerate(picks):
        print(i, p["title"], "seed", p["seed"])


if __name__ == "__main__":
    main()
