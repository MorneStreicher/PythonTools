from threading import Thread
from morne.sdk.comms.SAP import SAP
from morne.sdk.comms.Endpoint import Endpoint
from morne.sdk.app.Log import Log

import threading
import asyncore
import socket
import time
import traceback
import morne.sdk.perfcounters.Counter as Counter
import morne.sdk.perfcounters.PerfCounters as PerfCounters
import morne.sdk.perfcounters.StopWatch as StopWatch


class AsyncCoreTCPClientSAP(SAP):
    def __init__(self, name, queue, host, port, endpoint_filter_factory):
        SAP.__init__(self, name, queue, endpoint_filter_factory)
        self._map_local = {}
        self._host = host
        self._port = port
        self._thread = None

        #
        #
        #
        self.PERF_TIME_CONNECT_TIME = Counter.TimeCounter(\
            "SAP:%s" % self.name(),\
            "Connect time",\
            "Time to connect")
        PerfCounters.PerfCounters.ApplicationCounters.register_counter(self.PERF_TIME_CONNECT_TIME)

    def map_local(self):
        return self._map_local

    def host(self):
        return self._host

    def port(self):
        return self._port

    def connect(self, endpoint_reference=None):
        endpoint = AsyncCoreTCPClientEndpoint(self, ("localhost", 0), (self.host(), self.port()), endpoint_reference)
        return endpoint

    def start(self):
        self._thread = AsyncCoreTCPClientSAPThread(self)
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
            ep._client.close()

        # Remove counters local to this class
        PerfCounters.PerfCounters.ApplicationCounters.remove_counter(self.PERF_TIME_CONNECT_TIME)

        # Let the base class do its cleanup
        SAP.stop(self)

    def __str__(self):
        return "<AsyncCoreTCPClientSAP; name = %s>" % (self.name())

#
#
#


class AsyncCoreTCPClientEndpoint(Endpoint):
    def __init__(self, sap, local_address, remote_address, endpoint_reference):
        Endpoint.__init__(self, sap, endpoint_reference)

        self._local_address = local_address
        self._remote_address = remote_address
        self._is_connected = False
        self._sap = sap

        self.sap().add_endpoint(self)

        self._sw_connect_time = StopWatch.StopWatch.start_new()
        self._client = Client(self.sap(), self)

    def sap(self):
        return self._sap

    def local_address(self):
        return self._local_address

    def remote_address(self):
        return self._remote_address

    def send_data_to_remote(self, data):
        self._client.append_buffer(data)

    def close(self):
        self._is_connected = False
        self._client._do_close()
        self._sap.remove_endpoint(self)

    def is_connected(self, data):
        return self._is_connected

    def handle_connect(self):
        self._is_connected = True
        self._sw_connect_time.stop()
        self.sap().PERF_TIME_CONNECT_TIME.apply(self._sw_connect_time)
        self.sap()._fire_connect_event(self)

    def handle_disconnect(self, reason):
        self._is_connected = False
        self._sap.remove_endpoint(self)
        self.sap()._fire_disconnect_event(self, reason)

    def __str__(self):
        return "<AsyncCoreTCPClientEndpoint; id = %s; local address = %s; remote address = %s; sap = %s>" % (self.id(), self.local_address(), self.remote_address(), self.sap())


#
#
#


class Client(asyncore.dispatcher):
    def __init__(self, sap, endpoint):
        asyncore.dispatcher.__init__(self, map=sap.map_local())

        self._sap = sap
        self._endpoint = endpoint
        self._buffer = ""
        self._is_closed = False
        self._lock = threading.RLock()

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.connect((sap.host(), sap.port()))

    def sap(self):
        return self._sap

    def readable(self):
        return True

    def writable(self):
        return True

    def _do_close(self):
        self._is_closed = True

    def handle_connect(self):
        self._endpoint.handle_connect()

    def handle_read(self):
        data = self.recv(8192)
        if data:
            self._endpoint.handle_data_from_remote(data)

    def handle_write(self):
        with self._lock:
            if len(self._buffer) > 0:
                self.send(self._buffer)
                self._buffer = ""

            if self._is_closed:
                #print "Closing client socket"
                self._endpoint.handle_disconnect("Initiated from local application")
                self.close()

    def handle_close(self):
        self._endpoint.handle_disconnect("Initiated from remote")
        self.close()

    def append_buffer(self, data):
        with self._lock:
            self._buffer = self._buffer + str(data)

    def handle_error(self):
        print traceback.format_exc()

#
#
#


class AsyncCoreTCPClientSAPThread(Thread):
    def __init__(self, sap):
        Thread.__init__(self, name="AsyncCoreTCPClientSAPThread:%s" % sap.name())
        self._sap = sap
        self.setDaemon(True)
        self._to_stop = False

    def set_stop_flag(self):
        self._to_stop = True

    def run(self):
        while True:
            try:
                asyncore.loop(map=self._sap.map_local(), count=10)
                time.sleep(0.01)
                if self._to_stop:
                    return
            except Exception, e:
                print traceback.format_exc()
                Log.log().critical("Error in AsynCore Thread for SAP [%s]: %s" % (self._sap.name(), traceback.format_exc()))

