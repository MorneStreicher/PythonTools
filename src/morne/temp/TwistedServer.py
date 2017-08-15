from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

import threading
import time

from twisted.python.log import startLogging
from sys import stdout

startLogging(stdout)

i = 0


class QOTD(Protocol):
    def connectionMade(self):
        global i
        i += 1
        print "Connected... %s" % (str(i))

    def connectionLost(self, reason):
        global i
        i -= 1
        print "Connected... %s" % (str(i))

    def dataReceived(self, data):
        self.transport.write(data)


class TestThread(threading.Thread):
    def run(self):
        time.sleep(1)
        print "Starting client endpoint"
        endpoint = TCP4ServerEndpoint(reactor, 51000, backlog=500)
        endpoint.listen(QOTDFactory("Message from the application..."))
        print "Done client endpoint"


class QOTDFactory(Factory):

    # This will be used by the default buildProtocol to create new protocols:
    protocol = QOTD

    def __init__(self, quote=None):
        self.quote = quote or 'An apple a day keeps the doctor away'

#endpoint = TCP4ServerEndpoint(reactor, 51000)
#endpoint.listen(QOTDFactory("Message from the application..."))

tt = TestThread()
tt.start()

print "BEFORE RUN"

reactor.suggestThreadPoolSize(50)
reactor.run()

print "AFTER RUN"