
from timechess_errors import *



def get_game_info(db, gameID):
    cursor = db.cursor()
    cursor.execute("SELECT white,black FROM games WHERE id=%s", (gameID,))
    rows = cursor.fetchall()
    cursor.close()

    if len(rows) != 1:
        raise TC_DBNotPossible()
    assert len(rows[0]) == 2

    return {"white": rows[0][0],
            "black": rows[0][1]}



def get_moves(db, gameID, include_seqNum=False):
    cursor = db.cursor()

#    # this version gets *all* history for a given game, and we'll post-filter it
#    # in Python.  This is probably good enough...
#    cursor.execute("""SELECT halfMoveNum,seqNum,move
#                      FROM moves
#                      WHERE gameID=%s
#                      ORDER BY halfMoveNum ASC, seqNum DESC""", (gameID,))



    # I *think* that this version will accomplish the same, with SQL-side
    # filtering.  I did some web searching, and the answers I found out there
    # were a lot more complex, so I'm not at all sure if this is correct, or
    # efficient.
    cursor.execute("""SELECT halfmoveNum,move,seqNum
                      FROM moves
                        NATURAL JOIN
                          (SELECT gameID, halfmoveNum, MAX(seqNum) seqNum
                           FROM moves
                           WHERE gameID=%s
                           GROUP BY gameID, halfmoveNum) tmp
                      ORDER BY halfmoveNum""", (gameID,))
    rows = cursor.fetchall()
    cursor.close()


    # NOTE: A move list always has a dummy None field at the head, so that we
    #       can trivial index into the array with 'halfmoveNum'
    retval = [None]
    for r in rows:
        assert len(r) == 3
        if len(retval) != r[0]:
            raise TC_DBNotPossible()

        if include_seqNum == False:
            retval.append(r[1])       # NOTE: the move is simple, just a string
        else:
            retval.append(r[1:3])     # NOTE: the move is a (str,seqNum) tuple

    return retval

