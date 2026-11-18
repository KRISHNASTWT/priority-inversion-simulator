import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pisim import POLICIES, pathfinder, simulate
from pisim.report import table


def run(policy, comm=10):
    return simulate(pathfinder(comm), POLICIES[policy])


class PathfinderScenario(unittest.TestCase):
    def test_plain_mutex_shows_priority_inversion(self):
        r = run("none")
        self.assertEqual((r.wait, r.finish, r.response, r.interference), (12, 17, 14, 9))
        self.assertTrue(r.missed)

    def test_priority_inheritance_fixes_it(self):
        r = run("inherit")
        self.assertEqual((r.wait, r.finish, r.response, r.interference), (3, 8, 5, 0))
        self.assertFalse(r.missed)

    def test_priority_ceiling_fixes_it(self):
        r = run("ceiling")
        self.assertEqual((r.wait, r.finish, r.response, r.interference), (2, 7, 4, 0))
        self.assertFalse(r.missed)

    def test_exact_timelines(self):
        sym = {"MET": "L", "COMM": "M", "BUS": "H"}
        expect = {"none": "LLMMMMMMMMMMLLLHHL",
                  "inherit": "LLMLLLHHMMMMMMMMML",
                  "ceiling": "LLLLLHHMMMMMMMMMML"}
        for p, s in expect.items():
            self.assertEqual("".join(sym[x] for x in run(p).running), s)


class Sweep(unittest.TestCase):
    def test_plain_response_grows_with_comm_length(self):
        for n in (1, 2, 4, 6, 8, 10, 14, 20):
            self.assertEqual(run("none", n).response, n + 4)

    def test_cures_do_not_depend_on_comm_length(self):
        for n in (1, 2, 4, 6, 8, 10, 14, 20):
            self.assertEqual(run("inherit", n).response, 5)
            self.assertEqual(run("ceiling", n).response, 4)

    def test_limit_passed_once_comm_exceeds_four_ticks(self):
        self.assertFalse(run("none", 4).missed)
        self.assertTrue(run("none", 5).missed)


class Invariants(unittest.TestCase):
    def test_every_task_finishes_and_cpu_never_idle(self):
        for p in POLICIES:
            r = run(p)
            self.assertEqual(set(r.done), {"MET", "COMM", "BUS"})
            self.assertEqual(len(r.running), 18)        # 6 + 10 + 2 ticks of work

    def test_report_mentions_reset_only_for_plain(self):
        out = table([run(p) for p in POLICIES])
        self.assertEqual(out.count("RESET"), 1)


if __name__ == "__main__":
    unittest.main()
