# common functions, used by multiple Flash applications in the timechess
# website.



import MySQLdb
import private_no_share_dangerous_passwords as pnsdp
SQL_DB = "timechess"

from Flask import g
   # NOTE: This Python module is *NOT* a Flask application, so it does
   #       *not* declare an app object!!!



def get_db():
    # the database connection is stored in the application context.  Contrary
    # to what the name implies, this really doesn't persist across requests;
    # rather, it's a single context, per-client-request, which can be shared
    # across requests if you happen to have *nested invocation*.
    #
    # So on every new HTTP operation, expect to open a new DB connection.
    #
    # TODO: investigate connection pooling and SQL Alchemy.  That seems to be
    #       the standard-of-choice for SQL databases in Flask.

    if not hasattr(g, "db"):
        g.db = MySQLdb.connect(host   = pnsdp.SQL_HOST,
                               user   = pnsdp.SQL_USER,
                               passwd = pnsdp.SQL_PASSWD,
                               db     = SQL_DB)
    return g.db



