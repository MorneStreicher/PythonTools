class CounterSet:
    def __init__(self, name):
        self._counters = {}
        self._name = name

    def name(self):
        return self._name

    def register_counter(self, counter):
        if self._counters.has_key(counter.full_name()):
            print "WARNING: Duplicate performance counter was registered: %s" % counter.full_name()
        else:
            self._counters[counter.full_name()] = counter

    def remove_counter(self, counter):
        if self._counters.has_key(counter.full_name()):
            del self._counters[counter.full_name()]
        else:
            print "WARNING: Performance counter was not registered, and could not be removed: %s" % counter.full_name()

    def counters(self):
        return self._counters

    def clear(self):
        for key in self._counters:
            self._counters[key].clear()

    def clone(self):
        clone = CounterSet(self.name())
        for key in self._counters:
            clone._counters[key] = self._counters[key].clone()
        return clone
