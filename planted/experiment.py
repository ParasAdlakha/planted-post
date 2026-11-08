"""Concurrent, resumable grid runner.

python -m planted.experiment --models gpt-4.1-mini gpt-5-mini --arms none benign hint direct --seeds 6
"""
from __future__ import annotations

import argparse
import json
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .agents import ROOT
from .run import episode_id, run_episode

OUT = ROOT / "results" / "episodes"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--arms", nargs="+", default=["none", "benign", "hint", "direct"])
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--seed0", type=int, default=0)
    ap.add_argument("--n", nargs="+", type=int, default=[8])
    ap.add_argument("--rounds", type=int, default=12)
    ap.add_argument("--possible", action="store_true", help="solvable-task control")
    ap.add_argument("--variant", default="plain")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    jobs = []
    for m in args.models:
        for arm in args.arms:
            for n in args.n:
                for s in range(args.seed0, args.seed0 + args.seeds):
                    eid = episode_id(m, arm, s, n, not args.possible, args.variant)
                    if not (OUT / f"{eid}.json").exists():
                        jobs.append((m, arm, s, n, eid))
    print(f"{len(jobs)} episodes to run", flush=True)
    t0 = time.time()

    def go(j):
        m, arm, s, n, eid = j
        ep = run_episode(m, arm, s, n_agents=n, rounds=args.rounds, impossible=not args.possible, variant=args.variant)
        (OUT / f"{eid}.json").write_text(json.dumps(ep, indent=1), encoding="utf-8")
        canary = len({l["agent"] for l in ep["log"] if l.get("canary")})
        return eid, canary, len(ep["reports"]), ep["seconds"]

    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(go, j): j for j in jobs}
        for f in as_completed(futs):
            done += 1
            try:
                eid, c, r, sec = f.result()
                print(f"[{done}/{len(jobs)} {time.time()-t0:.0f}s] {eid}: canary={c} reports={r} ({sec}s)", flush=True)
            except Exception:
                print(f"[{done}/{len(jobs)}] FAILED {futs[f][-1]}\n{traceback.format_exc()[-600:]}", flush=True)


if __name__ == "__main__":
    main()
