import time
import traceback
from threading import Thread

from twisted.internet import reactor

import morne.sdk.app.Log as Log

class ReactorThread(Thread):
    def __init__(self):
        Thread.__init__(self, name="TwistedReactorThread")
        self.setDaemon(False)

    def run(self):
        while True:
            try:
                print "Starting Twisted reactor..."
                reactor.run(installSignalHandlers=0)
                print "Exiting Twisted reactor..."
                time.sleep(1)
            except Exception, e:
                Log.log().critical("Twisted reactor thread error :%s" % traceback.format_exc())

