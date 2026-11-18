"""Tick-by-tick simulation of priority scheduling with one shared mutex.

Each task is a script of single characters:
    L = lock the mutex (takes no time)      U = unlock the mutex (takes no time)
    C = one tick of CPU work
A higher number means a higher priority. One tick = one time unit.
"""
from dataclasses import dataclass, field
from typing import List

from .policies import Policy


@dataclass
class Task:
    name: str
    priority: int
    release: int
    script: str
    symbol: str = ""

    def __post_init__(self):
        self.symbol = self.symbol or self.name[0]


@dataclass
class Scenario:
    tasks: List[Task]
    watched: str          # task whose deadline is checked (BUS)
    interferer: str       # medium task that causes the inversion (COMM)
    deadline: int         # watchdog limit in ticks after the watched task's release


@dataclass
class Result:
    scenario: Scenario
    policy: Policy
    running: List[str] = field(default_factory=list)          # task that ran in each tick
    watched_blocked: List[bool] = field(default_factory=list)  # was the watched task blocked?
    done: dict = field(default_factory=dict)                   # finish tick of each task

    @property
    def release(self):
        return next(t.release for t in self.scenario.tasks if t.name == self.scenario.watched)

    @property
    def finish(self):
        return self.done[self.scenario.watched]

    @property
    def response(self):
        return self.finish - self.release

    @property
    def wait(self):
        return sum(self.watched_blocked)

    @property
    def interference(self):
        """Ticks the medium task ran while the watched task was blocked."""
        return sum(1 for r, b in zip(self.running, self.watched_blocked)
                   if r == self.scenario.interferer and b)

    @property
    def missed(self):
        return self.response > self.scenario.deadline


def simulate(scenario: Scenario, policy: Policy) -> Result:
    tasks = {t.name: t for t in scenario.tasks}
    script = {n: t.script for n, t in tasks.items()}
    pc = {n: 0 for n in tasks}                           # position in each script
    eff = {n: t.priority for n, t in tasks.items()}      # effective priority
    ceiling = max(t.priority for t in tasks.values() if "L" in t.script)
    result = Result(scenario, policy)
    blocked, waiting, state = set(), [], {"owner": None}
    t = 0

    def grant(task):
        state["owner"] = task
        policy.on_acquire(eff, task, ceiling)

    def settle(task):
        """Carry out the zero-time lock/unlock steps of `task`."""
        while pc[task] < len(script[task]) and script[task][pc[task]] != "C":
            if script[task][pc[task]] == "L":
                if state["owner"] is None:
                    grant(task)
                    pc[task] += 1
                else:                                    # mutex is taken: wait
                    blocked.add(task)
                    waiting.append(task)
                    policy.on_block(eff, state["owner"], task)
                    return
            else:                                        # unlock
                state["owner"] = None
                eff[task] = tasks[task].priority         # drop any raised priority
                pc[task] += 1
                if waiting:                              # hand the lock to the best waiter
                    nxt = max(waiting, key=lambda w: eff[w])
                    waiting.remove(nxt)
                    blocked.discard(nxt)
                    grant(nxt)
                    pc[nxt] += 1
                    settle(nxt)
        if pc[task] == len(script[task]) and task not in result.done:
            result.done[task] = t

    while len(result.done) < len(tasks):
        for n, tk in tasks.items():
            if tk.release == t:
                settle(n)
        ready = [n for n, tk in tasks.items()
                 if tk.release <= t and n not in result.done and n not in blocked]
        run = max(ready, key=lambda n: eff[n])           # scheduler: highest effective priority
        result.running.append(run)
        result.watched_blocked.append(scenario.watched in blocked)
        pc[run] += 1
        t += 1
        settle(run)
    return result
