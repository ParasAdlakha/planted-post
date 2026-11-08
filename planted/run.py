"""Run one episode: N LLM agents in one shared sandbox for T rounds."""
from __future__ import annotations

import json
import random
import time
from concurrent.futures import ThreadPoolExecutor

from .agents import POSTS, SYSTEM, VARIANTS, chat, parse_action
from .sandbox import Sandbox

TREE = ["sbx-01", "sbx-02", "sbx-03", "sbx-04", "sbx-05", "sbx-06", "sbx-07", "sbx-08", "sbx-09", "sbx-10",
        "sbx-12", "sbx-13", "sbx-14", "sbx-15", "sbx-16", "sbx-17", "sbx-18", "sbx-19", "sbx-20", "sbx-21"]  # sbx-11 is the auditor


def run_episode(model: str, arm: str, seed: int, n_agents: int = 8, rounds: int = 10,
                impossible: bool = True, variant: str = "plain") -> dict:
    rng = random.Random(seed)
    agents = sorted(rng.sample(TREE, n_agents))
    sb = Sandbox(agents=agents, impossible=impossible, seed=seed, post_text=POSTS[arm])
    system = {a: SYSTEM.format(me=a, T=rounds) + VARIANTS[variant] for a in agents}
    convo = {a: [{"role": "system", "content": system[a]},
                 {"role": "user", "content": "Contents of /:\n" + sb.listing(a, "/") + f"\n\nStep 1 of {rounds}. Begin."}] for a in agents}
    turns: list[dict] = []
    usage = {"in": 0, "out": 0}
    t0 = time.time()

    def decide(a):
        text, u = chat(model, convo[a])
        return a, text, u

    with ThreadPoolExecutor(max_workers=n_agents) as ex:
        for rnd in range(1, rounds + 1):
            results = list(ex.map(decide, agents))
            order = agents[:]
            rng.shuffle(order)  # execution order within a round is random
            byname = {a: (t, u) for a, t, u in results}
            for a in order:
                text, u = byname[a]
                usage["in"] += u["in"]
                usage["out"] += u["out"]
                act = parse_action(text)
                if act is None:
                    obs = 'Your reply was not a valid JSON action. Reply with one JSON object, e.g. {"thought": "...", "action": "ls", "path": "/"}.'
                    sb.log.append({"round": rnd, "agent": a, "action": "unparseable", "path": ""})
                else:
                    obs = sb.step(a, rnd, act)
                turns.append({"round": rnd, "agent": a, "raw": text, "action": act, "obs": obs})
                convo[a].append({"role": "assistant", "content": text})
                tail = f"Step {rnd + 1} of {rounds}." if rnd < rounds else "No steps left."
                if a in sb.submissions:
                    tail += " (You have already submitted.)"
                convo[a].append({"role": "user", "content": f"Observation:\n{obs}\n\n{tail}"})

    return {
        "model": model, "arm": arm, "seed": seed, "n_agents": n_agents, "rounds": rounds,
        "impossible": impossible, "variant": variant, "agents": agents,
        "records": {a: list(v) for a, v in sb.record.items()},
        "post": POSTS[arm], "turns": turns, "log": sb.log, "board_history": sb.board_history,
        "board_final": sb.shared, "submissions": sb.submissions, "reports": sb.reports,
        "usage": usage, "seconds": round(time.time() - t0, 1),
    }


def episode_id(model, arm, seed, n_agents, impossible, variant):
    m = model.replace("/", "_")
    return f"{m}__{arm}__n{n_agents}__{'imp' if impossible else 'pos'}__{variant}__s{seed}"


if __name__ == "__main__":
    import sys
    ep = run_episode(sys.argv[1] if len(sys.argv) > 1 else "gpt-4.1-mini", "direct", 0, n_agents=4, rounds=6)
    print(json.dumps({k: ep[k] for k in ("submissions", "reports", "usage", "seconds")}, indent=1))
