from twisted.internet.protocol import Protocol, ClientFactory
from sys import stdout
import threading
import time

from morne.sdk.perfcounters.StopWatch import StopWatch

count = 0
total = 0

class Echo(Protocol):

    def __init__(self):
        self.sw_session = StopWatch.start_new()

    def connectionMade(self):
        self.transport.write("1")

    def dataReceived(self, data):
        x = int(data)
        x += 1
        #print x

        _self = self
        #def do_it():
        _self.transport.write(str(x))
        if x > 20:
            _self.sw_session.stop()
            print "Session time = %s" % _self.sw_session.total_ms()
            _self.transport.loseConnection()

        #reactor.callLater(0, do_it)

class EchoClientFactory(ClientFactory):
    def startedConnecting(self, connector):
        print 'Started to connect.'
        self.sw_connect = StopWatch.start_new()

    def buildProtocol(self, addr):
        print 'Connected.'
        global total
        total += 1
        print "Total = %s" % total
        return Echo()

    def clientConnectionLost(self, connector, reason):
        global count
        count -= 1
        self.sw_connect.stop()
        print "Connection lost, total time ms: %s" % self.sw_connect.total_ms()

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason

class TestThread(threading.Thread):
    def run(self):

        def do_connect():
            print "Connecting..."
            reactor.connectTCP("USERVER2", 50000, EchoClientFactory())

        while True:
            global count
            for x in range(count, 10000):
                global count
                count += 1
                reactor.callLater(0, do_connect)
            time.sleep(0.5)


class ReactorThread(threading.Thread):
    def run(self):
        reactor.run()


from twisted.internet import reactor

ReactorThread().start()
TestThread().start()







