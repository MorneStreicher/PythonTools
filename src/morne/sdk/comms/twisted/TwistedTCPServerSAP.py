from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol

from ReactorCaller import ReactorCaller
from morne.sdk.comms.Endpoint import Endpoint
from morne.sdk.comms.SAP import SAP

import morne.sdk.comms.twisted


class TwistedTCPServerSAP(SAP):
    def __init__(self, name, queue, host, port, endpoint_filter_factory):
        SAP.__init__(self, name, queue, endpoint_filter_factory)
        self._host = host
        self._port = port
        self._twistedport = None

        morne.sdk.comms.twisted.__start()

    def host(self):
        return self._host

    def port(self):
        return self._port

    def connect(self, endpoint_reference=None):
        raise Exception("Server SAPs does not support the connect() operation")

    def start(self):
        if not (self._twistedport is None):
            raise Exception("SAP [%s] is already started." % self.name())

        def do():
            self._twistedport = reactor.listenTCP(self._port, TwistedFactory(self), backlog=20000, interface=self._host)
        ReactorCaller.call(do)

    def stop(self):
        if self._twistedport is None:
            raise Exception("SAP [%s] is not started." % self.name())

        def do():
            self._twistedport.stopListening()
            self._twistedport = None
        ReactorCaller.call(do)

    def __str__(self):
        return "<TwistedTCPServerSAP; name = %s>" % (self.name())

#
#
#


class TwistedTCPServerEndpoint(Endpoint):
    def __init__(self, protocol, local_address, remote_address, endpoint_reference):
        self._protocol = protocol
        self._local_address = local_address
        self._remote_address = remote_address
        self._is_connected = True

        Endpoint.__init__(self, protocol.sap(), endpoint_reference)

    def local_address(self):
        return self._local_address

    def remote_address(self):
        return self._remote_address

    def send_data_to_remote(self, data):
        self._protocol._queue_data_to_send(data)

    def close(self):
        self._is_connected = False
        self._protocol._do_close()
        self._protocol.sap().remove_endpoint(self)

    def is_connected(self, data):
        return self._is_connected

    def __str__(self):
        return "<TwistedTCPServerEndpoint; id = %s; local address = %s; remote address = %s; sap = %s>" % \
               (self.id(), self.local_address(), self.remote_address(), self.sap())

#
#
#


class TwistedProtocol(Protocol):

    def __init__(self, sap):
        self._sap = sap
        self._endpoint = None
        self._close_reason = "Initiated from remote"

    def sap(self):
        return self._sap

    def connectionMade(self):
        local_address = self.transport.getHost()
        remote_address = self.transport.getPeer()
        self._endpoint = TwistedTCPServerEndpoint(self, local_address, remote_address, None)

        self.sap().add_endpoint(self._endpoint)
        self.sap()._fire_connect_event(self._endpoint)

    def connectionLost(self, reason):
        self.sap().remove_endpoint(self._endpoint)
        self.sap()._fire_disconnect_event(self._endpoint, "%s:%s" % (self._close_reason, str(reason)))
        self._endpoint = None

    def dataReceived(self, data):
        self._endpoint.handle_data_from_remote(data)

    def _queue_data_to_send(self, data):
        def do():
            self.transport.write(data)
        ReactorCaller.call(do)

    def _do_close(self):
        def do():
            self._close_reason = "Initiated from application"
            self.transport.loseConnection()
        ReactorCaller.call(do)

class TwistedFactory(Factory):
    def __init__(self, sap):
        self._sap = sap

    def buildProtocol(self, addr):
        p = TwistedProtocol(self._sap)
        p.factory = self
        return p


