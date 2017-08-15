import Queue
from threading import RLock

from morne.sdk.perfcounters.Counter import ValueCounter
from morne.sdk.perfcounters.PerfCounters import PerfCounters


class AppQueue(Queue.Queue):
    """
    A queue class, wrapping the Python Queue implementation. This implementation adds the ability to add
    performance counters (i.e. queue size) to the queue implementation.
    """

    def __init__(self, name):
        """
        Constructor.
        Args:
            name: The queue name

        Returns:
            Nothing
        """
        Queue.Queue.__init__(self)
        self._name = name
        self._size = 0

        self._size_lock = RLock()

        #
        # A performance counter to counter the number of events in the queue
        #
        self.PERF_VALUE_QUEUE_SIZE = ValueCounter(\
            "Queue:%s" % self.name(),\
            "Queue size",\
            "Number of events in queue")
        PerfCounters.ApplicationCounters.register_counter(self.PERF_VALUE_QUEUE_SIZE)

    def name(self):
        """
        Returns:
            The queue name
        """
        return self._name

    def stop(self):
        self.put(None)

    def put(self, event):
        """Put an item into the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until a free slot is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Full exception if no free slot was available within that time.
        Otherwise ('block' is false), put an item on the queue if a free slot
        is immediately available, else raise the Full exception ('timeout'
        is ignored in that case).
        """
        with self._size_lock:
            self._size += 1
            self.PERF_VALUE_QUEUE_SIZE.apply(self._size)

        Queue.Queue.put(self, event)

    def get(self, block=True, timeout=None):
        """Remove and return an item from the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until an item is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Empty exception if no item was available within that time.
        Otherwise ('block' is false), return an item if one is immediately
        available, else raise the Empty exception ('timeout' is ignored
        in that case).
        """

        r = Queue.Queue.get(self, block, timeout)
        if not (r is None):
            with self._size_lock:
                self._size -= 1
                self.PERF_VALUE_QUEUE_SIZE.apply(self._size)
        else:
            PerfCounters.ApplicationCounters.remove_counter(self.PERF_VALUE_QUEUE_SIZE)
        return r
