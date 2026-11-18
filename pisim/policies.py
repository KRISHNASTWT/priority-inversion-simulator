"""Locking policies for the shared mutex.

A policy only changes the *effective* priority of tasks; the scheduler always runs
the ready task with the highest effective priority.
"""


class Policy:
    name = ""
    label = ""

    def on_acquire(self, eff, task, ceiling):
        """Called when `task` gets the mutex."""

    def on_block(self, eff, owner, waiter):
        """Called when `waiter` asks for the mutex that `owner` holds."""


class PlainMutex(Policy):
    name, label = "none", "plain"            # no protection: priority inversion can happen


class PriorityInheritance(Policy):
    name, label = "inherit", "inherit"

    def on_block(self, eff, owner, waiter):
        # the holder takes the priority of the highest-priority waiter until it unlocks
        if eff[owner] < eff[waiter]:
            eff[owner] = eff[waiter]


class PriorityCeiling(Policy):
    name, label = "ceiling", "ceiling"

    def on_acquire(self, eff, task, ceiling):
        # the holder runs at the mutex's ceiling (highest priority of any user) from the start
        eff[task] = max(eff[task], ceiling)


POLICIES = {p.name: p for p in (PlainMutex(), PriorityInheritance(), PriorityCeiling())}
