import CounterSet


class PerfCounters:
    ApplicationCounters = CounterSet.CounterSet("Application Counters")

    SqlCounters = CounterSet.CounterSet("Sql Counters")


