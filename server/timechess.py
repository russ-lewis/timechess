
from flask import Flask, request, render_template, url_for, redirect, make_response, jsonify
app = Flask(__name__)

import MySQLdb
import passwords

import sessions
import oauth

from timechess_game import TimeChess_Game



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
    (sessionID, google_account) = sessions.get_session(db,
                                               lambda key: request.cookies.get(key),
                                               None,
                                               ["google_account"])

    return render_template("index.html", sessionID=sessionID, mail=google_account)



@app.route("/game/<int:gameID>/<int:pos>")
def game(gameID, pos):
    db = get_db()
    (sessionID, google_account) = sessions.get_session(db,
                                               lambda key: request.cookies.get(key),
                                               None,
                                               ["google_account"])

    # TODO: confirm that the game ID is valid.  Or should this be a function
    #       of the Javascript code???



    history = ["e4",  "e5", "Ng3", "Nc6"]

    game = TimeChess_Game()
    game.add_to_history("e4")
    game.add_to_history("e5")

    legal_moves = game.legal_moves_san()

    def piece_url(sym):
        color = 'l' if sym.isupper() else 'd'
        kind  = sym.lower()
        path  = "board_images/{}{}t60.png".format(kind,color)
        return url_for("static", filename=path)
    pieces = [ (piece_url(sym),x,y) for (x,y,sym) in game.piece_list_xy() ]

    return render_template("game.html",
                           gameID=gameID,
                           history=history, pos=pos,
                           legal_moves=legal_moves,
                           board=str(game.board), pieces=pieces)



@app.route("/move", methods=["POST"])
def move():
    return "Hello world"


