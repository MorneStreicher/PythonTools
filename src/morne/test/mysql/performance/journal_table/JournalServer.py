import argparse
import json

from morne.sdk.app.Application import Application, ApplicationConfig
from morne.sdk.app.Timer import Timer
from morne.sdk.comms.EndpointFilterNByteHeader import EndpointFilter4ByteHeader
from morne.sdk.comms.SimpleEndpointFilterFactory import SimpleEndpointFilterFactory
from morne.sdk.comms.asynccore.AsyncCoreTCPServerSAP import AsyncCoreTCPServerSAP
from morne.sdk.perfcounters import Counter, PerfCounters
from morne.sdk.sql.Sql import Sql


class JournalServer(Application):
    def __init__(self, _args):
        self.server_sap = None
        self.endpoint = None
        self.journal_count = 0

        config = ApplicationConfig.ApplicationConfig(filename=_args.config)
        Application.__init__(self, config)

        self.PERF_SQL_INSERT_DATA = Counter.TimeCounter( \
            "JournalServer", \
            "Journal Insert Time", \
            "Time to insert into journal table")

        PerfCounters.PerfCounters.SqlCounters.register_counter(self.PERF_SQL_INSERT_DATA)

    def get_application_name(self):
        return "MorneJournalServer"

    def on_start(self):
        Timer.create_timer(None, 1000, "ConnectionCount")

        self.server_sap = AsyncCoreTCPServerSAP(
            "Server SAP",
            self.queue(),
            "0.0.0.0",
            50000,
            SimpleEndpointFilterFactory(EndpointFilter4ByteHeader))
        self.server_sap.start()

    def is_service(self):
        return True

    def process_timer_event(self, timer):
        if timer.reference == "ConnectionCount":
            print "Server endpoint count = %s, Journal count = %s " % \
                  (self.server_sap.endpoint_count(), self.journal_count)
            Timer.create_timer(None, 1000, "ConnectionCount")

    def process_connect_event(self, event):
        self.endpoint = event.endpoint()

    def process_disconnect_event(self, event):
        self.endpoint = None

    def process_data_event(self, event):
        self._insert_db(event.data())
        self.journal_count += 1
        event.endpoint().send_data(event.data())

    def process_other_event(self, event):
        pass

    def _insert_db(self, json_str):
        obj = json.loads(json_str)

        # Insert the request message into a journal table
        sql = "INSERT INTO journal(uuid, description, date, debit_account, credit_account, amount) VALUES " \
              "(%(uuid)s, %(description)s, %(date)s, %(debit_account)s, %(credit_account)s, %(amount)s)"
        Sql.execute("journal", sql, obj, self.PERF_SQL_INSERT_DATA)



###############################################################################
# The application entry point
#

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Morne Journal Server')
    parser.add_argument('--config', help='configuration file name')
    args = parser.parse_args()

    if args.config is None:
        print "Invalid command line arguments."
        parser.print_usage()
        parser.exit()
    else:
        print "Starting application using configuration file [%s]." % args.config
        comm = JournalServer(args)
        comm.start()
