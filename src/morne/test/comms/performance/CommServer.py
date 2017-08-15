import argparse
import time

from morne.sdk.app.Application import Application, ApplicationConfig
from morne.sdk.app.Timer import Timer
from morne.sdk.comms.asynccore.AsyncCoreTCPServerSAP import AsyncCoreTCPServerSAP
from morne.sdk.comms.SimpleEndpointFilterFactory import SimpleEndpointFilterFactory
from morne.sdk.comms.EndpointFilterNByteHeader import EndpointFilter4ByteHeader
from morne.sdk.perfcounters import Counter, PerfCounters


class CommServer(Application):
    def __init__(self, _args):
        self.server_sap = None
        self.client_sap = None

        config = ApplicationConfig.ApplicationConfig(filename=_args.config)
        Application.__init__(self, config)

    def get_application_name(self):
        return "MorneCommServer"

    def on_start(self):
        Timer.create_timer(None, 1000, "ConnectionCount")

        self.server_sap = AsyncCoreTCPServerSAP("Server SAP", self.queue(), "0.0.0.0", 50000, SimpleEndpointFilterFactory(EndpointFilter4ByteHeader))
        # self.server_sap = TwistedTCPServerSAP("Server SAP", self.queue(), "0.0.0.0", 50000, SimpleEndpointFilterFactory(EndpointFilter4ByteHeader))
        self.server_sap.start()

    def is_service(self):
        return True

    def process_timer_event(self, timer):
        if timer.reference == "ConnectionCount":
            print "Server endpoint count = %s " % self.server_sap.endpoint_count()
            Timer.create_timer(None, 1000, "ConnectionCount")

    def process_connect_event(self, event):
        # print event
        pass

    def process_disconnect_event(self, event):
        # print event
        pass

    def process_data_event(self, event):
        # print event
        # event.endpoint().close()

        # Insert the request message into a test table
        #sql = "INSERT INTO table_1(data) VALUES (%s)"
        #Sql.Sql.execute("test", sql, [event.data()], CommServer.PERF_SQL_INSERT_DATA1)

        event.endpoint().send_data(event.data())

        def _do_close():
            # print "Closing endpoint"
            event.endpoint().close()

        Timer.create_callback(None, 5000, _do_close)

    def process_other_event(self, event):
        pass


#
# Sql performance counters
#

CommServer.PERF_SQL_INSERT_DATA1 = Counter.TimeCounter( \
    "CommServer", \
    "Data insert 1", \
    "Our insert data statement 1",
    True)

PerfCounters.PerfCounters.SqlCounters.register_counter(CommServer.PERF_SQL_INSERT_DATA1)

CommServer.PERF_SQL_INSERT_DATA2 = Counter.TimeCounter( \
    "CommServer", \
    "Data insert 2", \
    "Our insert data statement 2",
    True)

PerfCounters.PerfCounters.SqlCounters.register_counter(CommServer.PERF_SQL_INSERT_DATA2)

###############################################################################
# The application entry point
#

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Morne Comm Test Server')
    parser.add_argument('--config', help='configuration file name')
    args = parser.parse_args()

    if args.config is None:
        print "Invalid command line arguments."
        parser.print_usage()
        parser.exit()
        exit(1)
    else:
        print "Starting application using configuration file [%s]." % args.config
        comm = CommServer(args)
        comm.start()
