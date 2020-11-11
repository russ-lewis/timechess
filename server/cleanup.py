#! /usr/bin/python3

"""Run this, from time to time (maybe every 12 hours?) to perform periodic
   cleanup tasks.  Right now, all it does is to get right of old sessions from
   the 'sessions' table.  Maybe it will do more in the future.

   Have this run from the crontab.  TODO: Is there a crontab equivalent in
   Docker???
"""

import MySQLdb
import passwords

import sessions



def get_db():
    return MySQLdb.connect(host   = passwords.SQL_HOST,
                           user   = passwords.SQL_USER,
                           passwd = passwords.SQL_PASSWD,
                           db     = "timechess")



if __name__ == "__main__":
    db    = get_db()
    count = sessions.cleanup_old_sessions(db)

    print(f"Cleaned up {count} records")


