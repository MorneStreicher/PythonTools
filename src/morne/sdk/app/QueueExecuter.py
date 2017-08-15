import threading
import traceback

import Log
import morne.sdk.app.Timer as Timer
import morne.sdk.comms.ConnectEvent as ConnectEvent
import morne.sdk.comms.DataEvent as DataEvent
import morne.sdk.comms.DisconnectEvent as DisconnectEvent
from morne.sdk.perfcounters import PerfCounters, Counter, StopWatch


class QueueExecuter(threading.Thread):
    def __init__(self, name, queue):
        self._queue = queue
        threading.Thread.__init__(self, name=name)

        self.PERF_EVENT_TIME = Counter.TimeCounter(\
            "QueueExecuter:%s" % self.name,\
            "Event time",\
            "The time taken to process an event")

        PerfCounters.PerfCounters.ApplicationCounters.register_counter(self.PERF_EVENT_TIME)

    def queue(self):
        return self._queue

    def _cleanup(self):
        PerfCounters.PerfCounters.ApplicationCounters.remove_counter(self.PERF_EVENT_TIME)

    def run(self):
        while True:
            try:
                try:
                    event = self._queue.get()
                    if event is None:
                        Log.Log.log().debug("Received a None event on queue [%s]. Stopping the event processor [%s]" %
                                            (self._queue.name(), self.name))
                        self._cleanup()
                        return
                    try:
                        self.process_event(event)
                    except Exception, e2:
                        Log.Log.log().error("[%s] Error while processing event: %s. The stack trace is: %s" %
                                            (self.name, event, traceback.format_exc()))
                finally:
                    self._queue.task_done()
            except Exception, e:
                Log.Log.log().error("[%s] Error in event processor. The stack trace is: %s" %
                                    (self.name, traceback.format_exc()))

    def process_event(self, event):
        #
        # Log the event to the debug log
        #
        debug_msg = "[%s]: Process event: [%s]" % (self.name, event)
        Log.Log.log().debug(debug_msg)

        #
        # Process the event
        #
        sw = StopWatch.StopWatch.start_new()
        try:
            if isinstance(event, Timer.Timer):
                self._process_timer_event(event)
            elif isinstance(event, DataEvent.DataEvent):
                self.process_data_event(event)
            elif isinstance(event, ConnectEvent.ConnectEvent):
                self.process_connect_event(event)
            elif isinstance(event, DisconnectEvent.DisconnectEvent):
                self.process_disconnect_event(event)
            else:
                self.process_other_event(event)
        finally:
            sw.stop()
            QueueExecuter.PERF_EVENT_TIME.apply(sw)
            self.PERF_EVENT_TIME.apply(sw)

    def _process_timer_event(self, timer):
        if isinstance(timer.reference, Timer.Callback):
            timer.reference.callback()()
        else:
            self.process_timer_event(timer)

    def process_timer_event(self, timer):
        pass

    def process_connect_event(self, event):
        pass

    def process_disconnect_event(self, event):
        pass

    def process_data_event(self, event):
        pass

    def process_other_event(self, event):
        pass


#
# SDK Debug performance counters
#

QueueExecuter.PERF_EVENT_TIME = Counter.TimeCounter(\
    "GlobalQueueExecuter",\
    "Event time",\
    "The time taken to process an event")

PerfCounters.PerfCounters.ApplicationCounters.register_counter(QueueExecuter.PERF_EVENT_TIME)