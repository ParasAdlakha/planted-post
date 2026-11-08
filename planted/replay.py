"""Deterministic replay: rebuild each episode's sandbox from its seed, re-execute every logged
action in the logged order, and check that every observation matches the log.

  python -m planted.replay            # all episodes
  python -m planted.replay <file.json>

This is the "rerun button": the environment is a pure function of (seed, arm, condition, actions),
so anyone can verify a released log without an API key. Rerunning the *agents* needs the API and
gives new samples (temperature 1); rerunning the *environment* is exact.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from .agents import POSTS
from .analyze import EP_DIR
from .sandbox import Sandbox


def replay(ep: dict) -> tuple[int, int]:
    sb = Sandbox(agents=ep["agents"], impossible=ep["impossible"], seed=ep["seed"], post_text=POSTS[ep["arm"]])
    ok = bad = 0
    for t in ep["turns"]:  # turns are stored in execution order
        if t["action"] is None:
            continue
        obs = sb.step(t["agent"], t["round"], t["action"])
        if obs == t["obs"]:
            ok += 1
        else:
            bad += 1
    same = sb.submissions == ep["submissions"] and sb.shared == ep["board_final"]
    return ok, bad + (0 if same else 1)


def main():
    files = [Path(a) for a in sys.argv[1:]] or sorted(EP_DIR.glob("*.json"))
    tot_ok = tot_bad = 0
    bad_eps = []
    for f in files:
        ok, bad = replay(json.loads(f.read_text(encoding="utf-8")))
        tot_ok += ok
        tot_bad += bad
        if bad:
            bad_eps.append(f.name)
    print(f"replayed {len(files)} episodes: {tot_ok} observations matched, {tot_bad} mismatches")
    for b in bad_eps[:20]:
        print("  mismatch:", b)
    return 1 if tot_bad else 0


if __name__ == "__main__":
    sys.exit(main())
