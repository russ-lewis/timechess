
import random



# get_session()
#
# Parameters:
#
#     db - a MySQLdb connection (or equivalent).  This code will read the
#         table (see details below) and may actually update the table as
#         well; if so, this code will *COMMIT* (unless you set commit=False)
#
#     get_cookie - a function (probably a lambda) which can be used to
#         retrieve a cookie; the function must take a single parameter (the
#         cookie name) and return a string or None
#
#     fields - a tuple of strings, giving the fields that you want to read
#         from the table.  This function will return these values, in the
#         same order they are listed in this tuple.  If we have to create a
#         new record, then this will insert a new record into the 'sessions'
#         table; I will not provide values for any of these fields, and so
#         you must provide default values (maybe NULL?) in the database.
#
#     commit (default=True) - if true, will commit changes to the DB
#
# Returns:
#     A tuple, containing:
#         The session ID
#         Each of the fields requested in the 'fields' parameter
#         A boolean, indicating whether we need to set the "sessionID" cookie
#
# Database:
#
# This function assumes that there is a table named 'sessions', which contains
# the following fields:
#     sessionID - CHAR(64).  I will always set this, so you may use it as a
#                            primary key (if you want).
#     expiration - DATETIME.  I will always set this, so you may set it as
#                             NOT NULL if you want.
#     <various> - one field for each field listed in the 'fields' parameter.
#
# What this does:
#   - Reads the cookie (might be None)
#   - Confirms that the cookie gives a valid (non-expired) sesssion ID
#   - If sessionID is valid:
#       - Updates the expiration time
#   - If sessionID is not valid:
#       - Creates a new entry in the DB
#       - Creates a cookie



SESSION_EXPIRATION_OFFSET = "00:30:00"

def get_session(db, get_cookie, fields, commit=True):
    assert get_cookie is not None

    # turn the fields into a comma-separated list
    fields = ",".join(fields)

    sessionID = get_cookie("sessionID")

    if sessionID is not None:
        cursor = db.cursor()

        cursor.execute("SELECT "+fields+" FROM sessions WHERE sessionID=%s AND expiration>NOW()", (sessionID,))
        assert cursor.rowcount <= 1
        if cursor.rowcount == 1:
            field_vals = cursor.fetchall()[0]
        else:
            field_vals = None
        cursor.close()

        if field_vals is not None:
            cursor = db.cursor()
            cursor.execute("UPDATE sessions SET expiration=ADDTIME(NOW(),%s) WHERE sessionID=%s", (SESSION_EXPIRATION_OFFSET,sessionID))
            cursor.close()
            if commit:
                db.commit()
            return (sessionID,) + field_vals + (False,)

    # create a new session ID
    sessionID = "%064x" % random.randint(0, 16**64)

    cursor = db.cursor()
    cursor.execute("INSERT INTO sessions(sessionID,expiration) VALUES(%s,ADDTIME(NOW(),%s))", (sessionID,SESSION_EXPIRATION_OFFSET))
    assert cursor.rowcount == 1
    cursor.close()
    if commit:
        db.commit()

    # read the fields (which are their default values)
    cursor = db.cursor()
    cursor.execute("SELECT "+fields+" FROM sessions WHERE sessionID=%s", (sessionID,))
    assert cursor.rowcount == 1
    field_vals = cursor.fetchall()[0]
    cursor.close()

    return (sessionID,) + field_vals + (True,)



# see get_session() above for the database assumptions.  Call this function
# once in a while, to clean up old records.
def cleanup_old_sessions(db, commit=True):
    cursor = db.cursor()
    cursor.execute("DELETE FROM sessions WHERE expiration<NOW()");
    cursor.close()

    if commit:
        db.commit()


