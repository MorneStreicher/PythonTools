import time

from morne.sdk.app.Application import Application
from morne.sdk.app.Timer import Timer
from morne.sdk.comms.asynccore.AsyncCoreTCPClientSAP import AsyncCoreTCPClientSAP
from morne.sdk.perfcounters import Counter, StopWatch, PerfCounters


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
        return "CommClientForTwisted"

    def on_start(self):
        self.client_sap = AsyncCoreTCPClientSAP("Client SAP", self.queue(), "127.0.0.1", 51000, None)
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
        self._handle_data_send(event.endpoint())

    def _handle_data_send(self, endpoint):
        endpoint.msg_count += 1
        endpoint.send_data(str(endpoint.msg_count))
        endpoint._sw_data_sent = StopWatch.StopWatch.start_new()

    def process_disconnect_event(self, event):
        # print event
        Timer.create_callback(None, 100, self._handle_reconnect)

    def _handle_reconnect(self):
        if self.client_sap.endpoint_count() < 400:
            for x in range(self.client_sap.endpoint_count(), 400):
                if self.client_sap.endpoint_count() < 400:
                    ep = self.client_sap.connect()
                    ep.msg_count = 0

    def process_data_event(self, event):
        event.endpoint()._sw_data_sent.stop()
        self.PERF_TIMER_MESSAGE_RESPONSE.apply(event.endpoint()._sw_data_sent)

        if event.endpoint().msg_count > 100:
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