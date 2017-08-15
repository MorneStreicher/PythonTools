import ConnectionPool

#
# The global application wide handle to the SQL Connection Pool
#  Applications should use ideally the utility methods in the Sql class
#

connection_pool = ConnectionPool.ConnectionPool()

