import datetime
import threading

import pymysql
from morne.sdk.perfcounters import Counter, PerfCounters


class ConnectionPoolEntry:
    def __init__(self, name, connection):
        self._name = name
        self._connection = connection
        self._activity_time = None

        self.mark_activity()

    def connection(self):
        return self._connection

    def name(self):
        return self._name

    def mark_activity(self):
        self._activity_time = datetime.datetime.utcnow()


class ConnectionPool:
    def __init__(self):
        self._config = None
        self._connections_in = dict()
        self._connections_out = dict()
        self._lock = threading.RLock()

    def set_config(self, config):
        self._config = config

    def get_actual_db_name(self, db_name):
        config = self._config
        return config["database:%s.db" % db_name]

    def get_connection(self, name):
        config = self._config
        with self._lock:
            if not self._connections_in.has_key(name):
                self._connections_in[name] = list()

            if not self._connections_out.has_key(name):
                self._connections_out[name] = list()

            if len(self._connections_in[name]) == 0:
                conn = pymysql.connect(
                    host=config["database:%s.host" % name],
                    port=int(config["database:%s.port" % name]),
                    db=config["database:%s.db" % name],
                    user=config["database:%s.user" % name],
                    passwd=config["database:%s.password" % name],
                    cursorclass=pymysql.cursors.DictCursor)

                ConnectionPool.PERF_SQL_CONNS_CREATED.apply()

                # We do this to identify the connection when it is returned
                conn._connection_pool_entry = ConnectionPoolEntry(name, conn)

                self._connections_in[name].append(conn._connection_pool_entry)

            conn_entry = self._connections_in[name].pop()
            conn_entry.mark_activity()
            self._connections_out[name].append(conn_entry)

            ConnectionPool.PERF_SQL_CONNS_OUT.apply()

            return conn_entry.connection()

    def return_connection(self, connection, force_close=False):
        ConnectionPool.PERF_SQL_CONNS_IN.apply()

        connection_entry = connection._connection_pool_entry
        name = connection_entry.name()

        with self._lock:
            if not self._connections_in.has_key(name):
                self._connections_in[name] = list()

            if not self._connections_out.has_key(name):
                self._connections_out[name] = list()

            connection_entry.mark_activity()
            self._connections_out[name].remove(connection_entry)

            if force_close:
                ConnectionPool.PERF_EVENT_CONNS_CLOSED.apply()
                connection_entry.connection().close()
            else:
                self._connections_in[name].insert(0, connection_entry)


#
# SDK Debug performance counters
#

ConnectionPool.PERF_SQL_CONNS_OUT = Counter.CountCounter( \
    "SqlConnectionPool", \
    "Sql Connections handed out", \
    "Number of Sql connections handed out from the connection pool")

ConnectionPool.PERF_SQL_CONNS_IN = Counter.CountCounter( \
    "SqlConnectionPool", \
    "Sql Connections returned", \
    "Number of Sql connections returned to the connection pool")

ConnectionPool.PERF_SQL_CONNS_CREATED = Counter.CountCounter( \
    "SqlConnectionPool", \
    "Sql Connections created", \
    "Number of physical Sql connections created")

ConnectionPool.PERF_EVENT_CONNS_CLOSED = Counter.CountCounter( \
    "SqlConnectionPool", \
    "Sql Connections closed", \
    "Number of physical Sql connections closed")

PerfCounters.PerfCounters.ApplicationCounters.register_counter(ConnectionPool.PERF_SQL_CONNS_OUT)
PerfCounters.PerfCounters.ApplicationCounters.register_counter(ConnectionPool.PERF_SQL_CONNS_IN)
PerfCounters.PerfCounters.ApplicationCounters.register_counter(ConnectionPool.PERF_SQL_CONNS_CREATED)
PerfCounters.PerfCounters.ApplicationCounters.register_counter(ConnectionPool.PERF_EVENT_CONNS_CLOSED)
