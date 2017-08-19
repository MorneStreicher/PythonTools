import threading


class BaseCounter:
    def __init__(self, group, name, description):
        self._group = group
        self._name = name
        self._description = description
        self._full_name = self._group + ":" + self._name
        self._lock = threading.RLock()

    def full_name(self):
        return self._full_name

    def group(self):
        return self._group

    def name(self):
        return self._name

    def description(self):
        return self._description

    def lock(self):
        return self._lock

    def apply(self, value):
        raise NotImplemented()

    def get_values(self):
        raise NotImplemented()

    def clear(self):
        raise NotImplemented()

    def clone(self):
        raise NotImplemented()


class TimeCounter(BaseCounter):
    def __init__(self, group, name, description, include_min_max=False):
        BaseCounter.__init__(self, group, name, description)
        self._total_ms = 0
        self._min_ms = 0
        self._max_ms = 0
        self._count = 0
        self._include_min_max = include_min_max

    def apply(self, stopwatch_value):
        with self.lock():
            ms = stopwatch_value.total_ms()

            self._count += 1
            self._total_ms += ms

            if self._include_min_max:
                if self._min_ms is None:
                    self._min_ms = ms
                else:
                    self._min_ms = min(ms, self._min_ms)

                if self._max_ms is None:
                    self._max_ms = ms
                else:
                    self._max_ms = max(ms, self._max_ms)

    def get_values(self):
        result = []

        v1 = dict()
        v1["name"] = "Avg(ms)"
        v1["value"] = None
        if self._count > 0:
            v1["value"] = self._total_ms / self._count
        result.append(v1)

        v2 = dict()
        v2["name"] = "Count"
        v2["value"] = self._count
        result.append(v2)

        if self._include_min_max:
            v3 = dict()
            v3["name"] = "Min(ms)"
            v3["value"] = self._min_ms
            result.append(v3)

            v4 = dict()
            v4["name"] = "Max(ms)"
            v4["value"] = self._max_ms
            result.append(v4)

        return result

    def clear(self):
        with self.lock():
            self._total_ms = 0
            self._count = 0
            self._min_ms = None
            self._max_ms = None

    def clone(self):
        with self.lock():
            clone = TimeCounter(self.group(), self.name(), self.description(), self._include_min_max)
            clone._total_ms = self._total_ms
            clone._count = self._count
            clone._min_ms = self._min_ms
            clone._max_ms = self._max_ms
            return clone

class CountCounter(BaseCounter):
    def __init__(self, group, name, description):
        BaseCounter.__init__(self, group, name, description)
        self._count = 0

    def apply(self, value=None):
        with self.lock():
            self._count += 1

    def get_values(self):
        result = []

        v2 = dict()
        v2["name"] = "Count"
        v2["value"] = self._count
        result.append(v2)

        return result

    def clear(self):
        with self.lock():
            self._count = 0

    def clone(self):
        with self.lock():
            clone = CountCounter(self.group(), self.name(), self.description())
            clone._count = self._count
            return clone

class TotalCountCounter(BaseCounter):
    def __init__(self, group, name, description):
        BaseCounter.__init__(self, group, name, description)
        self._count = 0

    def apply(self, value=None):
        with self.lock():
            self._count += 1

    def set_initial_value(self, value):
        self._count = value

    def get_current_value(self):
        with self.lock():
            return self._count

    def get_values(self):
        result = []

        v2 = dict()
        v2["name"] = "Count"
        v2["value"] = self._count
        result.append(v2)

        return result

    def clear(self):
        pass

    def clone(self):
        with self.lock():
            clone = TotalCountCounter(self.group(), self.name(), self.description())
            clone._count = self._count
            return clone


class ValueCounter(BaseCounter):
    def __init__(self, group, name, description):
        BaseCounter.__init__(self, group, name, description)
        self._min_value = None
        self._max_value = None

    def apply(self, value):
        with self.lock():
            if value is not None:
                if self._min_value is None:
                    self._min_value = value
                    self._max_value = value
                else:
                    self._min_value = min(self._min_value, value)
                    self._max_value = max(self._max_value, value)

    def get_values(self):
        result = []

        v1 = dict()
        v1["name"] = "Min"
        v1["value"] = self._min_value
        result.append(v1)

        v2 = dict()
        v2["name"] = "Max"
        v2["value"] = self._max_value
        result.append(v2)

        return result

    def clear(self):
        with self.lock():
            self._min_value = None
            self._max_value = None

    def clone(self):
        with self.lock():
            clone = ValueCounter(self.group(), self.name(), self.description())
            clone._min_value = self._min_value
            clone._max_value = self._max_value
            return clone
