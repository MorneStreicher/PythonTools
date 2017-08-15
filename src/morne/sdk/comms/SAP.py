import threading
import traceback

import ConnectEvent
import DisconnectEvent
import EndpointFilterNull
import SimpleEndpointFilterFactory
import morne.sdk.app.Log as Log
import morne.sdk.perfcounters.Counter as Counter
import morne.sdk.perfcounters.PerfCounters as PerfCounters


class SAP:

    # A class member to allowing us to give endpoints unique id's, accross SAPs
    endpoint_instance_count = 0

    def __init__(self, name, queue, endpoint_filter_factory):
        Log.Log.log().debug("Creating SAP: %s" % name)
        self._name = name
        self._queue = queue
        self._endpoint_filter_factory = endpoint_filter_factory
        if self._endpoint_filter_factory is None:
            self._endpoint_filter_factory = \
                SimpleEndpointFilterFactory.SimpleEndpointFilterFactory(EndpointFilterNull.EndpointFilterNull)

        self._endpoints_lock = threading.RLock()
        self._endpoints = {}

        #
        #
        #
        self.PERF_COUNT_CONNECTS = Counter.CountCounter(\
            "SAP:%s" % self.name(),\
            "Connect events",\
            "Number of SAP connect events")
        PerfCounters.PerfCounters.ApplicationCounters.register_counter(self.PERF_COUNT_CONNECTS)

        self.PERF_COUNT_DISCONNECTS = Counter.CountCounter(\
            "SAP:%s" % self.name(),\
            "Disconnect events",\
            "Number of SAP disconnect events")
        PerfCounters.PerfCounters.ApplicationCounters.register_counter(self.PERF_COUNT_DISCONNECTS)

    def name(self):
        return self._name

    def queue(self):
        return self._queue

    def endpoint_filter_factory(self):
        return self._endpoint_filter_factory

    def add_endpoint(self, endpoint):
        with self._endpoints_lock:
            SAP.endpoint_instance_count += 1
            endpoint._id = SAP.endpoint_instance_count
            self._endpoints[endpoint.id] = endpoint

    def remove_endpoint(self, endpoint):
        with self._endpoints_lock:
            if self._endpoints.has_key(endpoint.id):
                del self._endpoints[endpoint.id]

    def endpoint_count(self):
        with self._endpoints_lock:
            return len(self._endpoints)

    def get_endpoint_by_id(self, id):
        with self._endpoints_lock:
            if self._endpoints.has_key(id):
                return self._endpoints[id]
            else:
                return None

    def get_endpoint_ids(self):
        with self._endpoints_lock:
            return self._endpoints.keys()

    def _fire_connect_event(self, endpoint):
        self.PERF_COUNT_CONNECTS.apply()

        #TODO, MORNE: Move this to QueueExecuter class??
        try: 
            endpoint.endpoint_filter().connected()
        except Exception, e:
                Log.log().critical("Error calling endpoint filter connected :%s" % traceback.format_exc())

        self.queue().put(ConnectEvent.ConnectEvent(endpoint))

    def _fire_disconnect_event(self, endpoint, reason):
        self.PERF_COUNT_DISCONNECTS.apply()

        try:
            endpoint.endpoint_filter().disconnected()
        except Exception, e:
                Log.log().critical("Error calling endpoint filter disconnected :%s" % traceback.format_exc())

        self.queue().put(DisconnectEvent.DisconnectEvent(endpoint, reason))

    def connect(self, endpoint_reference=None):
        raise NotImplementedError()

    def start(self):
        raise NotImplementedError()

    def stop(self):
        PerfCounters.PerfCounters.ApplicationCounters.remove_counter(self.PERF_COUNT_CONNECTS)
        PerfCounters.PerfCounters.ApplicationCounters.remove_counter(self.PERF_COUNT_DISCONNECTS)

