"""Charts (needs matplotlib): timeline of each policy and the COMM-length sweep."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .policies import POLICIES
from .scenarios import pathfinder
from .scheduler import simulate

TITLES = {"none": "Plain mutex", "inherit": "Priority inheritance", "ceiling": "Priority ceiling"}
STYLE = {"none": ("#c0392b", "o"), "inherit": ("#2e6fb5", "s"), "ceiling": ("#2a9d5c", "^")}
SWEEP = (1, 2, 4, 6, 8, 10, 14, 20)


def timeline_chart(path, comm_len=10):
    sc = pathfinder(comm_len)
    lanes = {t.name: i for i, t in enumerate(sorted(sc.tasks, key=lambda t: t.priority))}
    top = lanes[sc.watched]
    fig, axes = plt.subplots(3, 1, figsize=(7, 5), dpi=200, sharex=True)
    for ax, key in zip(axes, POLICIES):
        r = simulate(sc, POLICIES[key])
        for t, (run, blk) in enumerate(zip(r.running, r.watched_blocked)):
            ax.broken_barh([(t, 1)], (lanes[run] - .35, .7), facecolors="#1f2a3a", edgecolor="white", lw=.4)
            if blk:
                ax.broken_barh([(t, 1)], (top - .35, .7), facecolors="none", edgecolor="#777", hatch="////", lw=.3)
        ax.axvline(r.release + sc.deadline, color="#c0392b", ls="--", lw=1)
        ax.set_yticks(list(lanes.values()))
        ax.set_yticklabels(list(lanes.keys()), fontsize=8)
        verdict = "RESET" if r.missed else "OK"
        ax.set_title(f"{TITLES[key]}: {sc.watched} waits {r.wait}, response {r.response} ticks - {verdict}",
                     fontsize=9, fontweight="bold", loc="left",
                     color="#c0392b" if r.missed else "#1b6b34")
    axes[-1].set_xlabel("Time (ticks)   [dark = running, hatched = BUS blocked, red line = watchdog limit]")
    axes[-1].set_xticks(range(0, len(r.running) + 1, 2))
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def sweep_values(sweep=SWEEP):
    return {key: [simulate(pathfinder(n), POLICIES[key]).response for n in sweep] for key in POLICIES}


def sweep_chart(path, sweep=SWEEP):
    fig, ax = plt.subplots(figsize=(6, 4), dpi=200)
    for key, vals in sweep_values(sweep).items():
        ax.plot(sweep, vals, marker=STYLE[key][1], color=STYLE[key][0], lw=1.4, label=TITLES[key])
    ax.axhline(pathfinder().deadline, color="#444", ls="--", lw=1)
    ax.text(sweep[-1], pathfinder().deadline + .6, "watchdog limit (8 ticks)", ha="right", fontsize=8)
    ax.set_xlabel("COMM work (ticks)")
    ax.set_ylabel("BUS response time (ticks)")
    ax.set_title("Effect of the medium task's length", fontweight="bold")
    ax.grid(lw=.3, alpha=.6)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
