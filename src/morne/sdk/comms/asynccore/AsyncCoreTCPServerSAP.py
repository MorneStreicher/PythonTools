from threading import Thread
from morne.sdk.comms.SAP import SAP
from morne.sdk.comms.Endpoint import Endpoint

import threading
import asyncore
import socket
import traceback
import time


class AsyncCoreTCPServerSAP(SAP):
    def __init__(self, name, queue, host, port, endpoint_filter_factory):
        SAP.__init__(self, name, queue, endpoint_filter_factory)
        self._map_local = {}
        self._host = host
        self._port = port
        self._thread = None

    def map_local(self):
        return self._map_local

    def host(self):
        return self._host

    def port(self):
        return self._port

    def connect(self):
        raise Exception("Server SAPs does not support the connect() operation")

    def start(self):
        self._thread = AsyncCoreTCPServerSAPThread(self)
        self._thread.start()

    def stop(self):
        # Flag the worker thread to stop and wait for it
        self._thread.set_stop_flag()
        time.sleep(2)

        # close all the open connections in this SAP
        ids = list(self.get_endpoint_ids())
        for cur_id in ids:
            ep = self.get_endpoint_by_id(cur_id)
            ep.close()
            ep._connection_handler._sock.close()

        # Let the base class do its cleanup
        SAP.stop(self)

    def __str__(self):
        return "<AsyncCoreTCPServerSAP; name = %s>" % (self.name())

#
#
#


class AsyncCoreTCPServerEndpoint(Endpoint):
    def __init__(self, server, local_address, remote_address, endpoint_reference):
        self._server = server
        self._local_address = local_address
        self._remote_address = remote_address
        self._is_connected = True

        Endpoint.__init__(self, server.sap(), endpoint_reference)

    def sap(self):
        return self._sap

    def local_address(self):
        return self._local_address

    def remote_address(self):
        return self._remote_address

    def send_data_to_remote(self, data):
        self._connection_handler._queue_data_to_send(data)

    def close(self):
        self._is_connected = False
        self._connection_handler._do_close()
        self._sap.remove_endpoint(self)

    def is_connected(self, data):
        return self._is_connected

    def handle_close(self):
        self._is_connected = False
        self.sap().remove_endpoint(self)
        self.sap()._fire_disconnect_event(self, "Initiated from remote")

    def __str__(self):
        return "<AsyncCoreTCPServerEndpoint; local address = %s; remote address = %s; sap = %s>" % (self.local_address(), self.remote_address(), self.sap())

#
#
#


class ConnectionHandler(asyncore.dispatcher):
    def __init__(self, endpoint, sock, sap):
        self._endpoint = endpoint
        self._sap = sap
        self._sock = sock
        self._is_closed = False
        self._data_to_send = ""

        self._endpoint._connection_handler = self

        self._lock = threading.RLock()

        asyncore.dispatcher.__init__(self, sock, self._sap.map_local())

    def sap(self):
        return self._sap

    def _do_close(self):
        with self._lock:
            self._is_closed = True

    def _queue_data_to_send(self, data):
        with self._lock:
            if len(self._data_to_send) == 0:
                self._data_to_send = data
            else:
                self._data_to_send += str(data)

    def handle_read(self):
        data = self.recv(8*1024)
        if data:
            self._endpoint.handle_data_from_remote(data)

        if self._is_closed:
            print "Close socket, local disconnect"
            self._sock.close()

    def handle_write(self):
        with self._lock:
            if not (self._data_to_send is None):
                self.send(self._data_to_send)
                self._data_to_send = ""

    def handle_close(self):
        #print "In handle close : Close connection: %s" % repr(self._endpoint.remote_address())
        self._endpoint.handle_close()
        self.close()
#
#
#


class Server(asyncore.dispatcher):

    def __init__(self, sap):
        self._sap = sap

        asyncore.dispatcher.__init__(self, None, self._sap.map_local())
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((sap.host(), sap.port()))
        self.listen(5000)

    def sap(self):
        return self._sap

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            if self.sap().endpoint_count() < 500:
                sock, remote_address = pair
                local_address = (self._sap.host(), self._sap.port())
                endpoint = AsyncCoreTCPServerEndpoint(self, local_address, remote_address, None)
                handler = ConnectionHandler(endpoint, sock, self.sap())

                self.sap().add_endpoint(endpoint)
                self.sap()._fire_connect_event(endpoint)
            else:
                sock, remote_address = pair
                print "TODO: NBNBNB! More than 500 connections on server. closing the connection %s, %s" % remote_address
                sock.close()
        else:
            print "asyncore.dispatcher.accept () => pair is NONE. We can safely ignore this message."

    def stop(self):
        self.close()


#
#
#


class AsyncCoreTCPServerSAPThread(Thread):
    def __init__(self, sap):
        Thread.__init__(self, name="AsyncCoreTCPServerSAPThread:%s" % sap.name())
        self._sap = sap
        self._server = None
        self._to_stop = False
        self.setDaemon(True)

    def set_stop_flag(self):
        self._to_stop = True

    def run(self):
        self._server = Server(self._sap)
        while True:
            try:
                asyncore.loop(map=self._sap.map_local(), count=10)
                time.sleep(0.01)
                if self._to_stop:
                    self._server.stop()
                    return
            except Exception, e:
                print "SAP ERROR, SERVER: %s" % traceback.format_exc()

