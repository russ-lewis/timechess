
from flask import Flask, request, render_template, url_for, redirect, make_response, jsonify
app = Flask(__name__)

import MySQLdb
import passwords

import sessions
import oauth

from timechess_game import TimeChess_Game

from timechess_standard_queries import *
from timechess_errors           import *



# this forces all traffic to HTTPS
@app.before_request
def force_ssl():
    if request.url.startswith("http://"):
        dest = request.url.replace("http://", "https://", 1)
        return redirect(dest, code=301)   # 301: Moved Permanently



def get_db():
    if "db_conn" not in dir(request):
        request.db_conn = MySQLdb.connect(host   = passwords.SQL_HOST,
                                          user   = passwords.SQL_USER,
                                          passwd = passwords.SQL_PASSWD,
                                          db     = "timechess")
    return request.db_conn



@app.route("/")
def index():
    db = get_db()
    (sessionID, google_account, set_cookie) = sessions.get_session(db,
                                               lambda key: request.cookies.get(key),
                                               ["google_account"])

    retval = render_template("index.html", sessionID=sessionID, mail=google_account)
    if set_cookie:
        retval.set_cookie("sessionID", sessionID)
    return retval



@app.route("/game/<int:gameID>/<int:halfMoveNum>")
def game(gameID, halfMoveNum):
    db = get_db()
    (sessionID, google_account, set_cookie) = sessions.get_session(db,
                                               lambda key: request.cookies.get(key),
                                               ["google_account"])

    # TODO: confirm that the game ID is valid.  Or should this be a function
    #       of the Javascript code???



    history = ["e4",  "e5", "Ng3", "Nc6"]

    game = TimeChess_Game()
    game.add_to_history("e4")
    game.add_to_history("e5")

    legal_moves = sorted(game.legal_moves_san())

    def piece_url(sym):
        color = 'l' if sym.isupper() else 'd'
        kind  = sym.lower()
        path  = "board_images/{}{}t60.png".format(kind,color)
        return url_for("static", filename=path)
    pieces = [ (piece_url(sym),x,y) for (x,y,sym) in game.piece_list_xy() ]

    retval = make_response(render_template("game.html",
                                           gameID=gameID,
                                           history=history, halfMoveNum=halfMoveNum,
                                           legal_moves=legal_moves,
                                           board=str(game.board), pieces=pieces))
    if set_cookie:
        retval.set_cookie("sessionID", sessionID)
    return retval



@app.route("/move", methods=["POST"])
def move():
    db = get_db()
    (sessionID, google_account, set_cookie) = sessions.get_session(db,
                                               lambda key: request.cookies.get(key),
                                               ["google_account"])


# TODO: move the '++' suffix out of the 'moves' table, and add a 'status' field to games.  This will allow us to check, trivially, if one side or the other has won, which will simplify a lot of checks.


    # did they pass the required variables?
    if "gameID" not in request.form or "hmNum" not in request.form or "move" not in request.form:
        TODO
    gameID      = int(request.form["gameID"])
    halfMoveNum = int(request.form["hmNum" ])
    newMove     =     request.form["move"  ]

    if gameID <= 0 or halfMoveNum <= 0 or len(newMove) == 0:
        TODO

    # is the current logged-in person a player on the site?
    cursor = db.cursor()
    cursor.execute("SELECT players.id FROM sessions,players WHERE sessions.sessionID=%s AND players.google_account=sessions.google_account", (sessionID,))
    rows = cursor.fetchall()
    cursor.close()
    if len(rows) != 1:
        TODO
    playerID = rows[0][0]

    # get basic game info.  Only a player in the game can play, and they can
    # only choose their own moves.
    cursor = db.cursor()
    cursor.execute("SELECT white,black FROM games WHERE id=%s", (gameID,))
    rows = cursor.fetchall()
    cursor.close()
    if len(rows) != 1:
        TODO
    wh,bl = rows[0]
    assert wh != bl

    # is the player not in the game?
    if playerID not in (wh,bl):
        TODO

    # is the player attempting to move for the other side?
    if playerID == wh:
        if halfMoveNum % 2 != 1:
            TODO
    else:
        if halfMoveNum % 2 != 0:
            TODO

    # get the list of moves from the database.  This will report only a
    # *single* move for each halfMoveNum (the most recent one), but it will
    # include the seqNum for each, since that is useful later.  Note that this
    # is only a DB search; it does *NOT* know which of these moves might be
    # invalidated.  This does *NOT* look for checkmate anywhere - it returns
    # the *entire* history, even if there is a checkmate in the middle.
    #
    # Also note that the first element is always None, so that the first
    # halfMove - numbered 1 for user convenience - will be in slot [1] of the
    # returned list.  Thus, an empty list is invalid, but a list with only one
    # element is valid; that simply means that the game has no moves.  (If you
    # ask it for an invalid game ID, this is what you will get - it does *NOT*
    # validate that the gameID is valid.  But that's no worry in this code,
    # since we validated the gameID above.)
    #
    # Note that each element (save the None in [0]) is a tuple: (move,seqNum)
    moves = get_moves(db, gameID, include_seqNum=True)

    # is the move too advanced - no connection to it in the history?
    if halfMoveNum > len(moves):
        TODO

    # is there already a checkmate, anywhere in the move list?  Or any
    # end-of-game marker at all?
    if move_list_has_game_end(moves):
        TODO

    # have we already had too many alterations to that move (our DB table can
    # only hold seqNums up to 9).  Note that this is also useful, even if the
    # user is not doing anything bad, since we'll need to *set* the seqNum in
    # the new row we insert soon.
    assert type(moves[halfMoveNum][1]) == int   # did we remember to conver it?
    if moves[halfMoveNum][1] == 9:
        TODO

    # is the move in question a "Pass"?  If so, then the player has lost the
    # chance to move, and can never change it.
    if moves[halfMoveNum][0] == "Pass":
        TODO


    return str((gameID,halfMoveNum,newMove, sessionID,google_account, playerID, wh,bl, moves))

    # looks like (hopefully) we're going to add an update to the database.  To
    # ensure that this is a legal move (and to check for checkmate as a result
    # of this new move), we need to build a Board object which represents the
    # current state (as of the position where we're making a change).
    board = build_board_from_moves(moves[:halfMoveNum])

    # check to see if the move is legal, given the history that comes
    # before it in the game.
    if not board.move_is_legal(newMove):
        TODO

    # apply the move, and check for checkmate.
    board.apply_move(newMove)

    if board.is_checkmate:
        newMove += "++"
        TODO
    if board.game_ended:
        TODO


    # all looks good.  Record the new move into the DB.  (Note the cool SQL
    # nested query, to set the debug_seq field...this is a new thing for me to
    # try out, and I sure hope I get it right!) - Russ, 26 Jun 2020
    cursor = db.cursor()
    cursor.execute("INSERT INTO moves(gameID,halfMoveNum,seqNum,move,debug_seq) "+
                   "VALUES(%s,%s,%s,%s," +
                          "1+SELECT MAX(debug_seq) FROM moves)",
                   (gameID, halfMoveNum, 1+moves[halfMoveNum][1], newMove))
    if cursor.rowcount != 1:
        TODO
    cursor.close()


    # yay, all done!
    db.commit()

    # TODO: wake up Redis server, let it know that a new move has happened.


    retval = redirect(url_for("game",
                              gameID      = gameID,
                              halfMoveNum = halfMoveNum+1))
    if set_cookie:
        retval.set_cookie("sessionID", sessionID)
    return retval



#def get_moves(db, gameID):
#    cursor = db.cursor()
#    cursor.execute("SELECT halfMoveNum,seqNum,move FROM moves WHERE gameID=%s ORDER BY halfMoveNum DESC, seqNum DESC", (gameID,))
#    rows = cursor.fetchall()
#    cursor.close()
#
#    retval = [None]
#
#    # we want to collapse any entries which have duplicate halfMoveNum fields.
#    rows = list(rows)
#    while len(rows) > 0:
#        assert rows[-1][1] == 1
#        while len(rows) > 1 and rows[-2][0] == rows[-1][0]:
#            assert rows[-2][1] > rows[-1][1]
#            rows.pop()    # discard one entry
#
#        # sanity check that the halfMoveNum values are sequential; assuming
#        # that's correct, we pop the most move & seqNum into the list of moves
#        # we're going to return
#        assert rows[-1][0] == len(retval)
#        retval.append( rows.pop()[1:][::-1] )
#
#    return retval



def move_list_has_game_end(moves):
    for move in moves[1:]:
        if move[-2:] == "++":
            return True
        if move in ["WhRes","BlRes","Draw"]:
            return True
    return False



def build_board_from_move_list(moves):
    game = TimeChess_Game()

    if moves[-1] == "Pending":
        moves = moves[:-1]

    for move in moves[1:]:
        game.add_to_history(move)
        if game.is_game_over():
            break

    return game



@app.route("/ugly/<int:gameID>/<int:halfmoveNum>")
def ugly(gameID, halfmoveNum):
    try:
        db = get_db()
        (sessionID, google_account, set_cookie) = sessions.get_session(db,
                                                   lambda key: request.cookies.get(key),
                                                   ["google_account"])

        try:
            vals = get_game_info(db, gameID)
            wh = vals["white"]
            bl = vals["black"]
        except TC_IDNotFoundError:
            TODO

        moves = get_moves(db, gameID)
        max_move = len(moves)-1

        moves_display = ""
        for i in range(1, len(moves), 2):
            moves_display += "{:2d}. ".format(i/2)

            pair = moves[i:i+2]
            if len(pair) == 2:
                moves_display += "{:8s}{}".format(*pair)
            else:
                moves_display += pair[0]
            moves_display += "\n"
        moves_display = moves_display[:-1]

        if len(moves)-1 < halfmoveNum:
            TODO
        if max_move > halfmoveNum:
            moves = moves[:halfmoveNum+1]

        game = build_board_from_move_list(moves)

        return render_template("ugly.html",
                               board       = game.get_simple_drawing(),
                               moves       = moves_display,
                               gameID      = gameID,
                               halfmoveNum = halfmoveNum,
                               max_move    = max_move)

    except TC_DBImpossibleError:
        TODO




@app.route("/rest", methods=["GET"])
def rest_root():
    return render_template("rest_root.html")

@app.route("/rest/games", methods=["GET"])
def rest_games():
    TODO   # each game should be listed by its *current* position (including half move num)

@app.route("/rest/games", methods=["POST"])
def rest_create_game():
    TODO

@app.route("/rest/games/<int:gameID>", methods=["GET"])
def rest_game_redirect_to_cur_move():
    TODO

@app.route("/rest/games/<int:gameID>/<int:halfMoveNum>", methods=["GET"])
def rest_game():
    TODO

@app.route("/rest/games/<int:gameID>", methods=["POST"])
def rest_make_new_move():
    TODO

@app.route("/rest/games/<int:gameID>/history", methods=["GET"])
def rest_game_history():
    TODO

@app.route("/rest/games/<int:gameID>/<int:halfMoveNum>", methods=["PUT"])
def rest_change_old_move():
    TODO



@app.route("/rest/players", methods=["GET"])
def rest_players():
    TODO

@app.route("/rest/players", methods=["POST"])
def rest_create_player():
    TODO


