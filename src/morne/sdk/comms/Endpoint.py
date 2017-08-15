from DataEvent import DataEvent
from morne.sdk.app.Log import Log
import threading


class Endpoint:
    def __init__(self, sap, endpoint_reference):
        self._sap = sap
        self._endpoint_filter = sap.endpoint_filter_factory().new_endpoint_filter(self)
        self._id = None
        self._endpoint_reference = endpoint_reference

    def sap(self):
        return self._sap

    def id(self):
        return self._id

    def endpoint_reference(self):
        return self._endpoint_reference

    def endpoint_filter(self):
        return self._endpoint_filter

    def set_endpoint_reference(self, ref):
        self._endpoint_reference = ref

    def send_data(self, data):
        """
        Called by applications to send data via this endpoint. The data is first passed through the endpoint filter, before
        sent to the remote.
        Args:
            data: The data to be sent.

        Returns:
            Nothing
        """
        debug_msg = "[%s]: Sending data on endpoint id %s: [%s]" % (threading.current_thread().name, self.id(), data)
        Log.log().debug(debug_msg)
        r = self._endpoint_filter.handle_data_from_app(data)

    def send_data_to_remote(self, data):
        raise NotImplementedError()

    def send_data_to_app(self, data):
        self.sap().queue().put(DataEvent(self, data))

    def handle_data_from_remote(self, data):
        r = self._endpoint_filter.handle_data_from_remote(data)

    def close(self, data):
        raise NotImplementedError()

    def is_connected(self, data):
        # NB: This method is currently not reliably implemented. Need more work in the
        # AsyncCore and Twisted implementations
        raise NotImplementedError()

