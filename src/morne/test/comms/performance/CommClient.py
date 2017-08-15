from morne.sdk.app.Application import Application
from morne.sdk.app.Timer import Timer
from morne.sdk.comms.asynccore.AsyncCoreTCPClientSAP import AsyncCoreTCPClientSAP
from morne.sdk.comms.twisted.TwistedTCPClientSAP import TwistedTCPClientSAP
from morne.sdk.comms.SimpleEndpointFilterFactory import SimpleEndpointFilterFactory
from morne.sdk.comms.EndpointFilterNByteHeader import EndpointFilter4ByteHeader
from morne.sdk.perfcounters import Counter, StopWatch, PerfCounters
import time
import random


class CommClient(Application):
    def __init__(self):
        self.client_sap = None
        Application.__init__(self, None)

        #
        #
        #
        self.PERF_TIMER_MESSAGE_RESPONSE = Counter.TimeCounter(\
            "CommClient",\
            "Message response time",\
            "Time to receive echo from server")
        PerfCounters.PerfCounters.ApplicationCounters.register_counter(self.PERF_TIMER_MESSAGE_RESPONSE)

        self.PERF_COUNT_INVALID_RESPONSE = Counter.CountCounter(\
            "CommClient",\
            "Invalid response data from server",\
            "Count of invalid response data from server")
        PerfCounters.PerfCounters.ApplicationCounters.register_counter(self.PERF_COUNT_INVALID_RESPONSE)

    def get_application_name(self):
        return "MorneCommClient"

    def on_start(self):
        self.client_sap = AsyncCoreTCPClientSAP("Client SAP", self.queue(), "127.0.0.1", 50000, SimpleEndpointFilterFactory(EndpointFilter4ByteHeader))
        self.client_sap.start()

        Timer.create_timer(None, 1000, "ConnectionCount")

        # Start a new connection to our server
        #self.client_sap.connect()
        self._handle_reconnect()

    def is_service(self):
        return True

    def process_timer_event(self, timer):
        if timer.reference == "ConnectionCount":
            print "Client endpoint count = %s " % self.client_sap.endpoint_count()

            # Restart the timer
            Timer.create_timer(None, 1000, "ConnectionCount")

    def process_connect_event(self, event):
        #print event
        #print event.endpoint().endpoint_reference()
        event.endpoint().msg_count = 0
        self._handle_data_send(event.endpoint())
        #pass

    def _handle_data_send(self, endpoint):
        def do():
            msg = "This is a message from the client, endpoint id = %s" % str(endpoint.id())
            endpoint.msg_count += 1
            endpoint.send_data(msg)
            endpoint._sw_data_sent = StopWatch.StopWatch.start_new()

        Timer.create_callback(None, 1000 + random.random()*0, do)

    def process_disconnect_event(self, event):
        #print event
        Timer.create_callback(None, 100, self._handle_reconnect)

    def _handle_reconnect(self):
        for x in range(self.client_sap.endpoint_count(), 500):
            if self.client_sap.endpoint_count() < 500:
                ep = self.client_sap.connect("Client Reference %s" % x)

    def process_data_event(self, event):
        msg = "This is a message from the client, endpoint id = %s" % str(event.endpoint().id())
        if event.data() != msg:
            print "Invalid response : [%s], expected [%s]" % (event.data(), msg)
            self.PERF_COUNT_INVALID_RESPONSE.apply()

        event.endpoint()._sw_data_sent.stop()
        self.PERF_TIMER_MESSAGE_RESPONSE.apply(event.endpoint()._sw_data_sent)

        if event.endpoint().msg_count > 4:
            event.endpoint().close()
        else:
            self._handle_data_send(event.endpoint())


    def process_other_event(self, event):
        pass

###############################################################################
# The application entry point
#

if __name__ == "__main__":
    comm = CommClient()
    comm.start()