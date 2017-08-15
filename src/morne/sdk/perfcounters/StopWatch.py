import time


class StopWatch:
    def __init__(self):
        self._start_time = time.time() * 1000
        self._end_time = 0

    def stop(self):
        self._end_time = time.time() * 1000

    def total_ms(self):
        if self._end_time == 0:
            self.stop()

        return self._end_time - self._start_time

    @staticmethod
    def start_new():
        return StopWatch()