import argparse
import os

import jinja2
from morne.sdk.app.Application import Application, ApplicationConfig
from morne.sdk.app.Log import Log
from morne.sdk.sql.Sql import Sql


class GenerateDataDictionaryApp(Application):
    def __init__(self, args):
        config = ApplicationConfig.ApplicationConfig(filename=args.config)
        print repr(config._config)
        Application.__init__(self, config)
        self._args = args

    def start_performance_counters(self):
        pass

    def get_application_name(self):
        return "GenerateDataDictionary"

    def on_start(self):
        sql = """SELECT * FROM information_schema.`TABLES`"""
        result = Sql.query("db", sql)
        for cur in result:
            self._do_table(cur["TABLE_SCHEMA"], cur["TABLE_NAME"])

    def _do_table(self, database_name, table_name):
        Log.log().info("Generating table: %s.%s" % (database_name, table_name))
        sql = """SELECT * FROM information_schema.`COLUMNS` c
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY c.ORDINAL_POSITION"""
        result = Sql.query("db", sql, (database_name, table_name))

        env = jinja2.Environment(loader=jinja2.FileSystemLoader(["./"]))
        template = env.get_template("DDTableTemplate.html")
        result = template.render(database_name=database_name, table_name=table_name, result=result)

        try:
            os.makedirs(os.path.join("output", database_name) )
        except:
            pass

        with open(os.path.join("output", database_name, table_name+".html"), "w+") as f:
            f.write(result)

###############################################################################
# The run method
#

def run():
    parser = argparse.ArgumentParser(description='Data Dictionary Generator')
    parser.add_argument('--config', help='configuration file name')
    parser.add_argument('--database', help='database name')
    args = parser.parse_args()

    if args.config is None:
        print "Invalid command line arguments."
        parser.print_usage()
        parser.exit()
    else:
        print "Starting application using configuration file [%s]. " % args.config
        g = GenerateDataDictionaryApp(args)
        g.start()

###############################################################################
# The application entry point
#

if __name__ == "__main__":
    run()
