import argparse
import random

import morne.sdk.app.Log as Log
from morne.sdk.app.Application import Application, ApplicationConfig
from morne.sdk.app.Timer import Timer
from morne.sdk.perfcounters import Counter, PerfCounters
from morne.sdk.sql.Sql import Sql


class StoragEngineTest(Application):
    def __init__(self, _args):
        self.server_sap = None
        self.endpoint = None
        self.journal_count = 0

        config = ApplicationConfig.ApplicationConfig(filename=_args.config)
        Application.__init__(self, config)

        self.PERF_SQL_INSERT_DATA = Counter.TimeCounter( \
            "StorageEngineTest", \
            "Table Insert Time", \
            "Time to insert into table")

        self.PERF_SQL_UPDATE_DATA = Counter.TimeCounter( \
            "StorageEngineTest", \
            "Table Update Time", \
            "Time to update existing row in table")

        self.PERF_SQL_TOTAL_ROW_COUNT = Counter.TotalCountCounter( \
            "StorageEngineTest", \
            "Total row count", \
            "Total count of entries in the test table")

        PerfCounters.PerfCounters.ApplicationCounters.register_counter(self.PERF_SQL_INSERT_DATA)
        PerfCounters.PerfCounters.ApplicationCounters.register_counter(self.PERF_SQL_UPDATE_DATA)
        PerfCounters.PerfCounters.ApplicationCounters.register_counter(self.PERF_SQL_TOTAL_ROW_COUNT)

    def get_application_name(self):
        return "StorageEngineTest"

    def _do_insert_update_work(self):
        Log.Log.log().info("Starting insert / update worker...")

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
            sql = "INSERT INTO test_table(varchar_1, varchar_2, varchar_3, varchar_4, varchar_5, varchar_6, varchar_7, varchar_8, varchar_9, varchar_10, varchar_11, varchar_12, varchar_13, varchar_14, varchar_15, varchar_16, varchar_17, varchar_18, varchar_19, varchar_20, " \
                  "float_1, float_2, float_3, float_4, float_5, float_6, float_7, float_8, float_9, float_10, float_11, float_12, float_13, float_14, float_15, float_16, float_17, float_18, float_19, float_20," \
                  "index_1, index_2, index_3, index_4, index_5) VALUES " \
                  "(%(varchar_1)s, %(varchar_2)s, %(varchar_3)s, %(varchar_4)s, %(varchar_5)s, %(varchar_6)s, %(varchar_7)s, %(varchar_8)s, %(varchar_9)s, %(varchar_10)s, %(varchar_11)s, %(varchar_12)s, %(varchar_13)s, %(varchar_14)s, %(varchar_15)s, %(varchar_16)s, %(varchar_17)s, %(varchar_18)s, %(varchar_19)s, %(varchar_20)s, " \
                  "%(float_1)s, %(float_2)s, %(float_3)s, %(float_4)s, %(float_5)s, %(float_6)s, %(float_7)s, %(float_8)s, %(float_9)s, %(float_10)s, %(float_11)s, %(float_12)s, %(float_13)s, %(float_14)s, %(float_15)s, %(float_16)s, %(float_17)s, %(float_18)s, %(float_19)s, %(float_20)s," \
                  "%(index_1)s, %(index_2)s, %(index_3)s, %(index_4)s, %(index_5)s)"
            Sql.execute("test_database", sql, values, self.PERF_SQL_INSERT_DATA)
            self.PERF_SQL_TOTAL_ROW_COUNT.apply()

            # Do the update, if we need to
            perc_to_update = int(self.application_config().get_application_setting("PercentageToUpdate", "50"))
            if random.randint(0, 100) <= perc_to_update:
                id_to_update = self.PERF_SQL_TOTAL_ROW_COUNT.get_current_value() - 7000000
                sql = "UPDATE test_table SET float_1 = float_1 + 1, float_2 = float_2 + 1, float_3 = float_3 + 1 WHERE id = %s" % id_to_update
                Sql.execute("test_database", sql, values, self.PERF_SQL_UPDATE_DATA)

    def _dump_table_status(self):
        r = Sql.query("test_database", "SHOW TABLE STATUS ")
        Log.Log.log().info("Table status: %s" % repr(r))
        Timer.create_callback(None, 60000, self._dump_table_status)

    def on_start(self):
        # Get the existing row count
        self.PERF_SQL_TOTAL_ROW_COUNT.set_initial_value(Sql.query("test_database", "SELECT COUNT(*) AS count FROM test_table")[0]["count"])

        # Start the workers
        for x in range(0, int(self.application_config().get_application_setting("ConcurrentCount", "1"))):
            Timer.create_callback(None, 1000, self._do_insert_update_work)

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
    parser = argparse.ArgumentParser(description='Storage Engine Test')
    parser.add_argument('--config', help='configuration file name')
    args = parser.parse_args()

    if args.config is None:
        print "Invalid command line arguments."
        parser.print_usage()
        parser.exit()
    else:
        print "Starting application using configuration file [%s]." % args.config
        comm = StoragEngineTest(args)
        comm.start()
