import datetime
import os
import sys
import threading
import traceback

import morne.sdk.app.Log as Log
from morne.sdk.app.AppQueue import AppQueue
from morne.sdk.app.QueueExecuter import QueueExecuter
from morne.sdk.app.Timer import Timer


class BasePublisher(QueueExecuter):
    def __init__(self, counter_set):
        QueueExecuter.__init__(self, "Event Publisher: %s" % counter_set.name(),
                                AppQueue("Event publisher: %s" % counter_set.name()))
        self._counter_set = counter_set
        Timer.create_timer(self.queue(), self.time_to_next_publish() * 1000, "Publish")

    def counter_set(self):
        return self._counter_set

    def _publish(self):
        clone = self._counter_set.clone()
        self._counter_set.clear()
        self._write_to_log(clone)
        self.publish(clone)

    def publish(self, counter_set):
        pass

    def time_to_next_publish(self):
        return 10

    def process_timer_event(self, timer):
        try:
            self._publish()
        finally:
            Timer.create_timer(self.queue(), self.time_to_next_publish() * 1000, "Publish")

    def _write_to_log(self, counter_set):
        result = "Performance counter set [%s] for the last %s seconds: %s" % \
                 (self._counter_set.name(), self.time_to_next_publish(), "\n")
        for cur_key in counter_set.counters():
            cur_counter = counter_set.counters()[cur_key]
            for cur_value in cur_counter.get_values():
                result += "\t\t %s:%s = %s%s" % (cur_counter.full_name(), cur_value["name"], cur_value["value"], "\n")
        Log.Log.log().debug(result)


class CsvFilePublisher(BasePublisher):
    def __init__(self, counter_set, application_name, output_folder):
        BasePublisher.__init__(self, counter_set)
        self._application_name = application_name
        self._output_folder = output_folder
        self.columns = ["Publish date/time"]
        self._log_start_datetime = datetime.datetime.now()

    def publish(self, counter_set):
        values = dict()
        values["Publish date/time"] = str(datetime.datetime.now())
        for cur_key in counter_set.counters():
            cur_counter = counter_set.counters()[cur_key]
            for cur_value in cur_counter.get_values():
                column_name = "%s:%s" % (cur_counter.full_name(), cur_value["name"])
                if column_name not in self.columns:
                    self.columns.append(column_name)
                values[column_name] = cur_value["value"]

        line = ""
        for cur in self.columns:
            if values[cur] is not None:
                line += str(values[cur])
            line += ","

        self._write_line(line)
        self._write_headers()
        self._dump_threads()

    def _write_line(self, line):
        path = os.path.join(self._output_folder, "perfcounters", self._application_name)
        try:
            os.makedirs(path)
        except:
            pass

        file_name = os.path.join(path, "%s-PerfCounters-%s-Data.csv" %
                                 (self._log_start_datetime.strftime("%Y%m%d%H%M%S"), self.counter_set().name()))
        f = open(file_name, "a+")
        f.write(line)
        f.write("\r")
        f.close()

    def _get_column_name(self, index):
        if index <= 25:
            return chr(index + 65)

        return "%s%s" % (self._get_column_name((index / 26) - 1), self._get_column_name((index % 26)))

    def _write_headers(self):
        path = os.path.join(self._output_folder, "perfcounters", self._application_name)
        try:
            os.makedirs(path)
        except:
            pass

        file_name = os.path.join(path, "%s-PerfCounters-%s-Headers.txt" %
                                 (self._log_start_datetime.strftime("%Y%m%d%H%M%S"), self.counter_set().name()))
        f = open(file_name, "w+")
        i = 0
        for x in self.columns:
            line = "%s - %s" % (self._get_column_name(i), x)
            f.write(line)
            f.write("\r")
            i += 1
        f.close()

    def _dump_threads(self):
        path = os.path.join(self._output_folder, "perfcounters", self._application_name)
        try:
            os.makedirs(path)
        except:
            pass

        file_name = os.path.join(path, "%s-StackTracesForAllThreads.txt" %
                                 (self._log_start_datetime.strftime("%Y%m%d%H%M%S")))
        f = open(file_name, "a+")
        try:
            code = []
            code.append("Current time: %s " % datetime.datetime.now())
            threads = {}
            for x in threading.enumerate():
                threads[x.ident] = x.name
            for threadId, stack in sys._current_frames().items():
                code.append("\t# ThreadID: %s:%s" % (threadId, threads[threadId]))
                for filename, lineno, name, line in traceback.extract_stack(stack):
                    code.append('\t\tFile: "%s", line %d, in %s' % (filename,
                                                                    lineno, name))
                    if line:
                        code.append("\t\t\t\t  %s" % (line.strip()))
            code.append("    **** END OF STACK TRACES ****")
            code.append("")
            code.append("")

            for line in code:
                f.write(line)
                f.write("\r")
        except:
            print "ERROR DUMPING THREADS: %s" % traceback.format_exc()
        f.close()
