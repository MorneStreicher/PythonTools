import os
import signal
import sys
import time
import traceback
import logging

import ApplicationConfig
import Log
import morne.sdk.app.AppQueue as AppQueue
import morne.sdk.app.AppQueueExecuter as AppQueueExecuter
import morne.sdk.sql
import TempLog
from morne.sdk.perfcounters.PerfCounters import PerfCounters
from morne.sdk.perfcounters.Publisher import CsvFilePublisher


class Application:
    """
    This Application class is the base class for event driven applications.
    """

    #
    # We keep a handle to the application instance. We expect only one application to run within a python process
    #
    instance = None

    def __init__(self, config):
        """
        Constructor.
        Args:
            config: An optional handle to an ApplicationConfig instance. If not specified, an empty ApplicationConfig
            instance will be used for the application configuration.
        Returns:
            Nothing
        """
        if config is None:
            self._application_config = ApplicationConfig.ApplicationConfig()
        else:
            self._application_config = config

        #
        # We keep a handle to the global Application instance in this static attribute, in case we need it. Only
        #  one application instance should exist (although we do not enforce it here)
        #
        Application.instance = self

        #
        # Setting the application suite output folder
        #
        try:
            os.makedirs(self.get_app_suite_output_folder())
        except:
            pass

        print "Setting the application output folder to [%s]" % self.get_app_suite_output_folder()

        #
        # Set up the global application log
        #
        log = TempLog.getLog(self.get_application_name(), pathToLogs=self.get_app_suite_output_folder())
        mapping = {
            "INFO" : logging.INFO,
            "DEBUG" : logging.DEBUG,
            "CRITICAL" : logging.CRITICAL,
            "ERROR" : logging.ERROR,
            "WARNING" : logging.WARNING,
        }
        level = self.application_config().get_application_setting("LogLevel", "DEBUG")
        log.setLevel(mapping[level])
        log.info("Application log was initialized to the level %s" % level)

        # Now we make the log available to the entire application by means of a static attribute
        Log.Log._set_application_log(log)

        #
        # The primary queue for the application instance
        #
        self._queue = AppQueue.AppQueue("Main Application Queue")

        #
        # The queue executers, serving the application instance
        #
        self._executers = None

    def start(self):
        """
        The main method that starts the application.

        Returns:
            Nothing
        """

        #
        # Start the performance counter publisher
        #
        self.start_performance_counters()

        #
        # Register signal handlers
        #
        self.register_signal_handlers()

        #
        # Start the queue executers
        #
        self._executers = self.get_queue_executers()
        for cur in self._executers:
            Log.Log.log().info("Starting up application queue executer: " + cur.name)
            cur.start()

        #
        #
        #
        Log.Log.log().info("Setting up database connection details")
        morne.sdk.sql.connection_pool.set_config(self._application_config.config())

        #
        #
        #
        Log.Log.log().info("Starting up the main application...")

        try:
            self.on_start()
        except:
            Log.Log.log().critical("Application generated an exception during startup and will now terminate. "
                                   "Exception:\r\n %s", traceback.format_exc())
            os._exit(1)

        #
        #
        #
        self.on_done()

    def application_config(self):
        """
        Returns:
             The instance to the application configuration. An instance of ApplicationConfig.ApplicationConfig.
        """
        return self._application_config

    def start_performance_counters(self):
        """
        Starts the performance counters for the application. Called just before the application's queue
        executers are started. The default implementation starts a CSV file performance counter publisher,
        publishing data every 10 seconds. Applications may override this method to create custom performance
        data publishers.

        Returns:
            Nothing
        """
        Log.Log.log().info("Starting application counter publisher")
        CsvFilePublisher(PerfCounters.ApplicationCounters, self.get_application_name(), self.get_app_suite_output_folder()).start()

    def get_application_name(self):
        """
        Returns:
            A user friendly name for this application instance
        """
        raise Exception("This method needs to return a friendly application name")

    @staticmethod
    def _def_control_cz_signal_handler(signal, frame):
        print ""
        print ""
        print "CONTROL-C/Z Detected. Forcefully terminating the Python machine. Signal = [%s]" % (signal)
        print ""
        print ""
        os._exit(1)

    def register_signal_handlers(self):
        """
        Registers the default application signal handlers. The default implementation listens for Ctrl-C and Ctrl-Z
        events, and forcefully exit the Python machine when detected. Applications may override this method to implement
        special signal handlers.

        Returns:
             Nothing
        """
        Log.Log.log().info("Register application signal handlers...")

        signal.signal(signal.SIGINT, Application._def_control_cz_signal_handler)
        try:
            # This signal only seems to be present on Linux. Not on Windows.
            signal.signal(signal.SIGTSTP, Application._def_control_cz_signal_handler)
        except:
            pass

    def queue(self):
        """
        Returns:
            A handle to the main application queue. In instance of AppQueue.
        """
        return self._queue

    def on_start(self):
        """
            Applications needs to override this method to do application specific initialization
        Returns:
            Nothing
        """
        pass

    def on_done(self):
        if self.is_service():
            Log.Log.log().info("The application indicated that it is a service. "
                               "The main application thread will now remain alive, but inactive.")
            while True:
                time.sleep(10)
        else:
            Log.Log.log().info("Done with application, since the on_done() method in the Application base class was called,"
                               "and the application indicated that it is not a service. Exiting now.")
            os._exit(0)

    def is_service(self):
        return False

    def get_queue_executers(self):
        """
        Returns:
            A list of AppQueueExecuter.AppQueueExecuter, not started. The default implementation
            makes use of the value returned by the method get_queue_executer_count().
        """
        result = []
        for x in range(1, self.get_queue_executer_count() + 1):
            p = AppQueueExecuter.AppQueueExecuter("App Executer %s" % x, self.queue(), self)
            result.append(p)
        return result

    def get_app_suite_output_folder(self):
         return os.path.join(self.get_app_suite_base_folder(), "MorneSDKOutput")

    def get_app_suite_base_folder(self):
        """
        Returns:
            The base folder for the application suite that this application instance belongs to.
        """
        if os.environ.get('MorneSDKOutputFolder'):
            return os.environ.get('MorneSDKOutputFolder')
        else:
            cur_folder = os.path.dirname(sys.argv[0])
            while True:
                if os.path.exists(os.path.join(cur_folder, "MORNE_BASE.TXT")):
                    return cur_folder
                prev_folder = cur_folder
                cur_folder = os.path.dirname(cur_folder)
                if cur_folder == prev_folder:
                    return cur_folder

    def get_queue_executer_count(self):
        """
        Returns:
            The number of queue executers to serve this application instance. The
            default value is 4.
        """
        return int(self.application_config().get_application_setting("ExecuterCount", "4"))

    def process_timer_event(self, timer):
        """
        Application needs to override this function to handle timer events.
        Args:
            timer:
                A handle to the timer event
        Returns:
            Nothing
        """
        pass

    def process_connect_event(self, event):
        """
        Application needs to override this function to handle SAP connection events.
        Args:
            event:
                A handle to the connect event
        Returns:
            Nothing
        """
        pass

    def process_disconnect_event(self, event):
        """
        Application needs to override this function to handle SAP disconnect events.
        Args:
            event:
                A handle to the disconnect event
        Returns:
            Nothing
        """
        pass

    def process_data_event(self, event):
        """
        Application needs to override this function to handle data events (i.e. data received from a SAP endpoint).
        Args:
            event:
                A handle to the data event
        Returns:
            Nothing
        """
        pass

    def process_other_event(self, event):
        """
        Application needs to override this function to handle all other types events (i.e. custom events).
        Args:
            event:
                A handle to the event
        Returns:
            Nothing
        """
        pass