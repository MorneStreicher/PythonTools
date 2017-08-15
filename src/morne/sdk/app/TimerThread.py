import datetime
import threading
import time
import traceback
from threading import Thread

from sortedcontainers import SortedListWithKey

import Log


class TimerThread(Thread):
    def __init__(self):

        def key_func(x):
            epoch = datetime.datetime.utcfromtimestamp(0)
            delta = x.expires - epoch
            return delta.total_seconds() * 1000

        self.key_func = key_func

        self.timers = SortedListWithKey(key=key_func)

        self.lock = threading.RLock()
        Thread.__init__(self, name="SDK Timer thread")
        self.setDaemon(True)

    def add(self, timer):
        with self.lock:
            self.timers.add(timer)

    def run(self):
        try:
            while True:
                now = datetime.datetime.utcnow()
                done = False
                with self.lock:
                    if len(self.timers) == 0:
                        done = True
                    while (not done) and (len(self.timers) > 0):
                        first = self.timers[0]
                        if first.expires < now:
                            if not first.is_stopped():
                                first.queue.put(first)
                            else:
                                # Timer was stopped. Do nothing
                                pass
                            del self.timers[0]
                        else:
                            done = True
                time.sleep(0.01)
        except Exception, e:
            Log.Log.log().error("Critical Error in SDK Timer thread: %s" % traceback.format_exc())
