"""Text report: comparison table and tick-by-tick timeline."""


def table(results):
    sc = results[0].scenario
    d = sc.deadline
    lines = [f"POLICY      {sc.watched}-WAIT  {sc.watched}-DONE  RESPONSE  "
             f"{sc.interferer}-WHILE-WAIT  WATCHDOG({d})"]
    for r in results:
        verdict = (f"RESET at t={r.release + d}" if r.missed
                   else f"OK ({d - r.response} spare)")
        lines.append(f"{r.policy.label:<10}{r.wait:>8}{r.finish:>10}{r.response:>10}"
                     f"{r.interference:>14}      {verdict}")
    return "\n".join(lines)


def timeline(results):
    sc = results[0].scenario
    sym = {t.name: t.symbol for t in sc.tasks}
    n = len(results[0].running)
    lines = ["tick   " + "".join(f"{t:>3}" for t in range(n))]
    for r in results:
        lines.append(f"{r.policy.label:<7}  " + "".join(f"{sym[x]:>3}" for x in r.running))
    lines.append("(" + ", ".join(f"{t.symbol} = {t.name}" for t in sc.tasks) + ")")
    return "\n".join(lines)
