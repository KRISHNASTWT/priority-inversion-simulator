from .scheduler import Scenario, Task


def pathfinder(comm_len: int = 10) -> Scenario:
    """Pathfinder-style scenario (numbers are illustrative, not real Pathfinder timings).

    MET  (low, 1)    ready at tick 0: lock bus, 5 ticks of work, unlock, 1 more tick
    COMM (medium, 2) ready at tick 2: `comm_len` ticks of work, never uses the bus
    BUS  (high, 3)   ready at tick 3: lock bus, 2 ticks of work, unlock
    BUS must finish within 8 ticks of its release or the watchdog resets the system.
    """
    return Scenario(
        tasks=[Task("MET", 1, 0, "L" + "C" * 5 + "U" + "C", "L"),
               Task("COMM", 2, 2, "C" * comm_len, "M"),
               Task("BUS", 3, 3, "LCCU", "H")],
        watched="BUS", interferer="COMM", deadline=8)
