import threading
import time
import traceback
from threading import Thread

from twisted.internet import reactor

import morne.sdk.app.Log as Log


class ReactorCaller(Thread):
    _list = []
    _lock = threading.RLock()

    def __init__(self):
        Thread.__init__(self, name="TwistedReactorCaller")

    @staticmethod
    def call(cl, *args, **kw):
        with ReactorCaller._lock:
            ReactorCaller._list.append((cl, args, kw))

    def run(self):

        def do_list_calling(_list):
            for cur in _list:
                cl, args, kw = cur
                cl(*args, **kw)

        while True:
            try:
                _list = None
                with ReactorCaller._lock:
                    _list = ReactorCaller._list
                    ReactorCaller._list = []

                reactor.callFromThread(do_list_calling, _list)
                time.sleep(0.01)

            except Exception, e:
                Log.log().critical("Twisted caller thread error :%s" % traceback.format_exc())

