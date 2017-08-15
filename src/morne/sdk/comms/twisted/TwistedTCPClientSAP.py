from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol

import morne.sdk.comms.twisted
import morne.sdk.perfcounters.Counter as Counter
import morne.sdk.perfcounters.PerfCounters as PerfCounters
import morne.sdk.perfcounters.StopWatch as StopWatch
from ReactorCaller import ReactorCaller
from morne.sdk.comms.Endpoint import Endpoint
from morne.sdk.comms.SAP import SAP


class TwistedTCPClientSAP(SAP):
    def __init__(self, name, queue, host, port, endpoint_filter_factory):
        SAP.__init__(self, name, queue, endpoint_filter_factory)
        self._host = host
        self._port = port
        self._twistedport = None

        morne.sdk.comms.twisted.__start()

        #
        #
        #
        self.PERF_TIME_CONNECT_TIME = Counter.TimeCounter(\
            "SAP:%s" % self.name(),\
            "Connect time",\
            "Time to connect")
        PerfCounters.PerfCounters.ApplicationCounters.register_counter(self.PERF_TIME_CONNECT_TIME)

    def host(self):
        return self._host

    def port(self):
        return self._port

    def connect(self, endpoint_reference=None):
        local_address = ("0.0.0.0", 0)
        remote_address = (self.host(), self.port())
        endpoint = TwistedTCPClientEndpoint(self, local_address, remote_address, endpoint_reference)
        endpoint._sw_connect_time = StopWatch.StopWatch.start_new()

        def do():
            iconnector = reactor.connectTCP(self.host(), self.port(), TwistedFactory(endpoint))
            endpoint._iconnector = iconnector

        ReactorCaller.call(do)

        return endpoint

    def start(self):
        pass

    def stop(self):
        pass

    def __str__(self):
        return "<TwistedTCPClientSAP; name = %s>" % (self.name())

#
#
#


class TwistedTCPClientEndpoint(Endpoint):
    def __init__(self, sap, local_address, remote_address, endpoint_reference):
        self._sap = sap
        self._local_address = local_address
        self._remote_address = remote_address
        self._is_connected = True
        self._closed_from_app = False

        self._protocol = None

        Endpoint.__init__(self, sap, endpoint_reference)

        self._sap.add_endpoint(self)

    def local_address(self):
        return self._local_address

    def remote_address(self):
        return self._remote_address

    def send_data_to_remote(self, data):
        self._protocol._queue_data_to_send(data)

    def close(self):
        self._is_connected = False
        self._closed_from_app = True
        self._protocol._do_close()
        self._protocol.endpoint().sap().remove_endpoint(self)

    def is_connected(self, data):
        return self._is_connected

    def __str__(self):
        return "<TwistedTCPClientEndpoint; id = %s; local address = %s; remote address = %s; sap = %s>" % \
               (self.id(), self.local_address(), self.remote_address(), self.sap())

#
#
#


class TwistedProtocol(Protocol):

    def __init__(self, endpoint):
        self._endpoint = endpoint
        self._endpoint._protocol = self

    def endpoint(self):
        return self._endpoint

    def connectionMade(self):
        self.endpoint().sap()._fire_connect_event(self.endpoint())

        self.endpoint()._sw_connect_time.stop()
        self.endpoint().sap().PERF_TIME_CONNECT_TIME.apply(self.endpoint()._sw_connect_time)

    def connectionLost(self, reason):
        # It seems that we can ignore this event
        pass

    def dataReceived(self, data):
        self._endpoint.handle_data_from_remote(data)

    def _queue_data_to_send(self, data):
        def do():
            self.transport.write(data)
        ReactorCaller.call(do)

    def _do_close(self):
        def do():
            self._endpoint._iconnector.disconnect()
        ReactorCaller.call(do)


class TwistedFactory(ClientFactory):
    def __init__(self, endpoint):
        self._endpoint = endpoint

    def endpoint(self):
        return self._endpoint

    def buildProtocol(self, addr):
        p = TwistedProtocol(self._endpoint)
        return p

    def startedConnecting(self, connector):
        pass

    def _get_close_reason(self):
        if self._endpoint._closed_from_app:
            return "Initiated from application"
        else:
            return "Initiated from remote"

    def clientConnectionLost(self, connector, reason):
        self.endpoint().sap().remove_endpoint(self._endpoint)
        self.endpoint().sap()._fire_disconnect_event(self._endpoint, "Connection lost:%s:%s" %
                                                     (self._get_close_reason(), str(reason)))

    def clientConnectionFailed(self, connector, reason):
        self.endpoint().sap().remove_endpoint(self._endpoint)
        self.endpoint().sap()._fire_disconnect_event(self._endpoint, "Connection failed:%s" % str(reason))



