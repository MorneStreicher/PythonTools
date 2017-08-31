import argparse
import json
import random
import pymongo
import json
from morne.sdk.perfcounters import StopWatch

import morne.sdk.app.Log as Log
from morne.sdk.app.Application import Application, ApplicationConfig
from morne.sdk.app.Timer import Timer
from morne.sdk.perfcounters import Counter, PerfCounters
from morne.sdk.sql.Sql import Sql

class CRUDTest(Application):
    def __init__(self, _args):
        self.server_sap = None
        self.endpoint = None
        self.journal_count = 0

        config = ApplicationConfig.ApplicationConfig(filename=_args.config)
        Application.__init__(self, config)

        self.PERF_SQL_INSERT_DATA = Counter.TimeCounter( \
            "MongoDbCrudTest", \
            "Table Insert Time", \
            "Time to insert into table",
            True)

        self.PERF_SQL_UPDATE_DATA = Counter.TimeCounter( \
            "MongoDbCrudTest", \
            "Table Update Time", \
            "Time to update existing row in table",
            True)

        self.PERF_SQL_LARGE_QUERY = Counter.TimeCounter( \
            "MongoDbCrudTest", \
            "Table Large Query Time", \
            "Time to perform large query",
            True)

        self.PERF_SQL_TOTAL_ROW_COUNT = Counter.TotalCountCounter( \
            "MongoDbCrudTest", \
            "Total row count", \
            "Total count of entries in the test table")

        PerfCounters.PerfCounters.ApplicationCounters.register_counter(self.PERF_SQL_INSERT_DATA)
        PerfCounters.PerfCounters.ApplicationCounters.register_counter(self.PERF_SQL_UPDATE_DATA)
        PerfCounters.PerfCounters.ApplicationCounters.register_counter(self.PERF_SQL_LARGE_QUERY)
        PerfCounters.PerfCounters.ApplicationCounters.register_counter(self.PERF_SQL_TOTAL_ROW_COUNT)

    def get_application_name(self):
        return "MongoDbCrudTest"

    def _do_insert_update_work(self):
        Log.Log.log().info("Starting insert / update worker...")
        conn = pymongo.MongoClient('10.0.0.50', 27017)

        while True:
            values = dict()
            for cur in range(1, 21):
                values["varchar_%s" % cur] = "This is a varchar value %s. This is additional data to the string value. This is additional data to the string value. " % cur
                values["float_%s" % cur] = cur

            # Populate index values
            values["index_1"] = str((random.randint(0, 9999999999) % 10000)).zfill(10)
            values["index_2"] = str((random.randint(0, 9999999999) % 5000)).zfill(10)
            values["index_3"] = str((random.randint(0, 9999999999) % 20000)).zfill(10)
            values["index_4"] = str((random.randint(0, 9999999999))).zfill(10)
            values["index_5"] = str((random.randint(0, 9999999999))).zfill(10)

            # Do the insert
            #jdoc = json.dumps(values)
            #print jdoc
            sw = StopWatch.StopWatch.start_new()
            conn.test_db.test_table.insert(values)
            sw.stop()
            self.PERF_SQL_INSERT_DATA.apply(sw)

            self.PERF_SQL_TOTAL_ROW_COUNT.apply()

            # Do the update, if we need to
            perc_to_update = int(self.application_config().get_application_setting("PercentageToUpdate", "50"))
            if random.randint(1, 100) <= perc_to_update:
                #id_to_update = self.PERF_SQL_TOTAL_ROW_COUNT.get_current_value() - 1000000
                #sql = "UPDATE test_table SET jdoc = JSON_SET(jdoc, '$.float_1', JSON_EXTRACT(jdoc, '$.float_1') + 1, '$.float_2', JSON_EXTRACT(jdoc, '$.float_2') + 1, '$.float_3', JSON_EXTRACT(jdoc, '$.float_3') + 1) WHERE id = %s" % id_to_update
                #Sql.execute("test_database", sql, values, self.PERF_SQL_UPDATE_DATA)
                print "TODO - UPDATE"

    def _do_large_query_work(self):
        Log.Log.log().info("Starting large query worker...")
        #while True:
        #    id = self.PERF_SQL_TOTAL_ROW_COUNT._count
        #    sql = "SELECT MAX(JSON_UNQUOTE(JSON_EXTRACT(jdoc, '$.float_10'))) FROM test_table WHERE id >= %s AND id <= %s" % (id-2000000, id)
        #    Sql.execute("test_database", sql, None, self.PERF_SQL_LARGE_QUERY)

    def _dump_table_status(self):
        pass
        Timer.create_callback(None, 60000, self._dump_table_status)

    def on_start(self):
        conn = pymongo.MongoClient('10.0.0.50', 27017)

        # Get the existing row count
        self.PERF_SQL_TOTAL_ROW_COUNT.set_initial_value(conn.test_db.test_table.count())

        # Start the workers
        for x in range(0, int(self.application_config().get_application_setting("ConcurrentCount", "1"))):
            Timer.create_callback(None, 1000, self._do_insert_update_work)

        # Start large query workers
        for x in range(0, int(self.application_config().get_application_setting("LargeQueryCount", "1"))):
            Timer.create_callback(None, 1000, self._do_large_query_work)

        # Dump table status every 60 seconds
        Timer.create_callback(None, 1000, self._dump_table_status)

    def is_service(self):
        return True

    def process_timer_event(self, timer):
        pass

    def process_other_event(self, event):
        pass

###############################################################################
# The application entry point
#

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Mongo DB CRUD Performance Test')
    parser.add_argument('--config', help='configuration file name')
    args = parser.parse_args()

    if args.config is None:
        print "Invalid command line arguments."
        parser.print_usage()
        parser.exit()
    else:
        print "Starting application using configuration file [%s]." % args.config
        comm = CRUDTest(args)
        comm.start()
