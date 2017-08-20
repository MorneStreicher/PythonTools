import traceback

import morne.sdk.sql
from morne.sdk.app.Log import Log
from morne.sdk.perfcounters import StopWatch

class Sql:
    def __init__(self):
        pass

    @staticmethod
    def query(db_name, sql, values={}, perf_counter=None):
        Log.log().debug("Executing SQL: [%s] with values [%s]" % (sql, repr(values)))
        result = []
        conn = morne.sdk.sql.connection_pool.get_connection(db_name)
        force_close = False
        sw = StopWatch.StopWatch.start_new()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, values)
            result = cursor.fetchall()
            conn.commit()

            sw.stop()
            if perf_counter:
                perf_counter.apply(sw)
        except Exception, e1:
            force_close = True
            Log.log().critical("Error executing SQL: [%s] with values [%s] - %s" % (sql, repr(values), traceback.format_exc()))
            conn.rollback()
            raise
        finally:
            morne.sdk.sql.connection_pool.return_connection(conn, force_close=force_close)

        return result

    @staticmethod
    def execute(db_name, sql, values={}, perf_counter=None):
        Log.log().debug("Executing SQL: [%s] with values [%s]" % (sql, repr(values)))
        result = 0
        conn = morne.sdk.sql.connection_pool.get_connection(db_name)
        force_close = False
        sw = StopWatch.StopWatch.start_new()
        try:
            cursor = conn.cursor()
            result = cursor.execute(sql, values)
            conn.commit()

            sw.stop()
            if perf_counter:
                perf_counter.apply(sw)
        except Exception, e1:
            force_close = True
            Log.log().critical("Error executing SQL: [%s] with values [%s]. Exception: %s" % (sql, repr(values), traceback.format_exc()))
            conn.rollback()
            raise
        finally:
            morne.sdk.sql.connection_pool.return_connection(conn, force_close=force_close)

        return result

    @staticmethod
    def table_exists(db_name, table_name):
        rs = Sql.query(db_name, "SELECT COUNT(*) AS count FROM INFORMATION_SCHEMA.TABLES AS T "
                                "WHERE T.TABLE_SCHEMA = %s AND T.TABLE_NAME = %s",
                       (morne.sdk.sql.connection_pool.get_actual_db_name(db_name), table_name))
        return rs[0]["count"] > 0

    @staticmethod
    def get_actual_db_name(db_name):
        return morne.sdk.sql.connection_pool.get_actual_db_name(db_name)

