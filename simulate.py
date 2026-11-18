#!/usr/bin/env python3
"""Priority Inversion Simulator - command line.

Examples
    python simulate.py --scenario pathfinder          # compare the three policies
    python simulate.py --policy inherit               # run one policy only
    python simulate.py --comm 4                       # shorter medium task
    python simulate.py --sweep                        # vary the medium task's length
    python simulate.py --plot                         # save charts to outputs/
"""
import argparse
import os

from pisim import POLICIES, pathfinder, simulate
from pisim.report import table, timeline


def main():
    ap = argparse.ArgumentParser(description="Priority inversion simulator")
    ap.add_argument("--scenario", default="pathfinder", choices=["pathfinder"])
    ap.add_argument("--policy", default="all", choices=["all", *POLICIES])
    ap.add_argument("--comm", type=int, default=10, help="COMM work in ticks (default 10)")
    ap.add_argument("--sweep", action="store_true", help="repeat for several COMM lengths")
    ap.add_argument("--plot", action="store_true", help="save timeline and sweep charts to outputs/")
    a = ap.parse_args()

    if a.comm == 10 and not a.sweep:
        print(f"$ python simulate.py --scenario {a.scenario}")
    keys = list(POLICIES) if a.policy == "all" else [a.policy]

    if a.sweep:
        from pisim.plot import SWEEP, sweep_values
        vals = sweep_values()
        print("BUS response time (ticks) for different COMM lengths; watchdog limit = 8")
        print("COMM   " + "".join(f"{POLICIES[k].label:>9}" for k in keys))
        for i, n in enumerate(SWEEP):
            print(f"{n:<7}" + "".join(f"{vals[k][i]:>9}" for k in keys))
    else:
        results = [simulate(pathfinder(a.comm), POLICIES[k]) for k in keys]
        print(table(results))
        print()
        print(timeline(results))

    if a.plot:
        from pisim.plot import sweep_chart, timeline_chart
        os.makedirs("outputs", exist_ok=True)
        timeline_chart("outputs/timeline.png", a.comm)
        sweep_chart("outputs/sweep.png")
        print("\nSaved outputs/timeline.png and outputs/sweep.png")


if __name__ == "__main__":
    main()
