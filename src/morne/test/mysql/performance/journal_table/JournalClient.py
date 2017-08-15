import argparse
import datetime
import json
import os
import random
import uuid

from morne.sdk.app.Application import Application, ApplicationConfig
from morne.sdk.app.Timer import Timer
from morne.sdk.comms.EndpointFilterNByteHeader import EndpointFilter4ByteHeader
from morne.sdk.comms.SimpleEndpointFilterFactory import SimpleEndpointFilterFactory
from morne.sdk.comms.asynccore.AsyncCoreTCPClientSAP import AsyncCoreTCPClientSAP
from morne.sdk.perfcounters import Counter, StopWatch, PerfCounters


class Posting:
    def __init__(self):
        self.uuid = str(uuid.uuid4())
        self.description = "Description for Journal ID %s" % self.uuid
        self.date = datetime.datetime.now().isoformat()
        self.debit_account = "%s" % (10000000000000 + random.randint(0, 99999999))
        self.credit_account = "%s" % (10000000000000 + random.randint(0, 99999999))
        self.amount = float(random.randint(0, 1000000)) / 100

    def to_json(self):
        obj = dict(self.__dict__)
        obj.pop("_sw_data_sent")
        return json.dumps(obj)


class JournalClient(Application):
    def __init__(self, args):
        self.client_sap = None
        self.client_endpoint = None
        self.outstanding_postings = {}
        self.journal_count = 0

        config = ApplicationConfig.ApplicationConfig(filename=args.config)
        Application.__init__(self, config)

        #
        #
        #
        self.PERF_TIMER_MESSAGE_RESPONSE = Counter.TimeCounter(\
            "JournalClient",\
            "Message response time",\
            "Time to receive response from server")
        PerfCounters.PerfCounters.ApplicationCounters.register_counter(self.PERF_TIMER_MESSAGE_RESPONSE)

        self.PERF_TIMER_IN_FLIGHT = Counter.ValueCounter(\
            "JournalClient",\
            "Journals in flight",\
            "Total number of journals in flight")
        PerfCounters.PerfCounters.ApplicationCounters.register_counter(self.PERF_TIMER_IN_FLIGHT)

        self.PERF_TIMER_JOURNAL_COUNT = Counter.CountCounter(\
            "JournalClient",\
            "Journals count",\
            "Total number of journals sent")
        PerfCounters.PerfCounters.ApplicationCounters.register_counter(self.PERF_TIMER_JOURNAL_COUNT)

    def get_application_name(self):
        return "MorneJournalClient"

    def get_queue_executer_count(self):
        return 4

    def on_start(self):
        self.client_sap = AsyncCoreTCPClientSAP(
            "Client SAP",
            self.queue(),
            "127.0.0.1",
            50000,
            SimpleEndpointFilterFactory(EndpointFilter4ByteHeader))
        self.client_sap.start()

        Timer.create_timer(None, 1000, "ConnectionCount")
        Timer.create_timer(None, 2000, "PostingSender")

        # Start a new connection to our server
        self._handle_reconnect()

    def is_service(self):
        return True

    def process_timer_event(self, timer):
        if timer.reference == "ConnectionCount":
            self.PERF_TIMER_IN_FLIGHT.apply(len(self.outstanding_postings))
            print "Client endpoint count = %s, outstanding posting count = %s, total journals = %s " % \
                  (self.client_sap.endpoint_count(), len(self.outstanding_postings), self.journal_count)
            # Restart the timer
            Timer.create_timer(None, 1000, "ConnectionCount")

        if timer.reference == "PostingSender":
            if self.client_endpoint:
                cur_outstanding_count = len(self.outstanding_postings)
                in_flight = int(self.application_config().get_application_setting("PostingsInFlight", 1))
                for x in xrange(cur_outstanding_count, in_flight):
                    posting = Posting()
                    posting._sw_data_sent = StopWatch.StopWatch.start_new()
                    self.outstanding_postings[posting.uuid] = posting
                    self.client_endpoint.send_data(posting.to_json())
                    self.journal_count += 1
                    self.PERF_TIMER_JOURNAL_COUNT.apply()
            # Restart the timer
            Timer.create_timer(None, int(self.application_config().get_application_setting("SendDelayMs", 100)), "PostingSender")

            if self.journal_count > int(self.application_config().get_application_setting("MaxJournalCount", 100)):
                print "Reached the maximum journal count. Exiting now."
                os._exit(1)

    def process_connect_event(self, event):
        self.client_endpoint = event.endpoint()

    def process_disconnect_event(self, event):
        self.outstanding_postings = {}
        self.client_endpoint = None
        Timer.create_callback(None, 10000, self._handle_reconnect)

    def _handle_reconnect(self):
        self.client_sap.connect()

    def process_data_event(self, event):
        obj = json.loads(event.data())
        posting = self.outstanding_postings[obj["uuid"]]
        posting._sw_data_sent.stop()
        self.PERF_TIMER_MESSAGE_RESPONSE.apply(posting._sw_data_sent)
        del self.outstanding_postings[obj["uuid"]]

    def process_other_event(self, event):
        pass

###############################################################################
# The application entry point
#

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Morne Journal Client')
    parser.add_argument('--config', help='configuration file name')
    args = parser.parse_args()

    if args.config is None:
        print "Invalid command line arguments."
        parser.print_usage()
        parser.exit()
    else:
        print "Starting application using configuration file [%s]." % args.config
        comm = JournalClient(args)
        comm.start()