
from flask import Flask, request, render_template, url_for, redirect, make_response, jsonify
app = Flask(__name__)

import MySQLdb

import passwords

import sessions
import oauth



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



@app.route("/game/<int:gameID>", defaults={"moveNum": -1})
@app.route("/game/<int:gameID>/<int:moveNum>")
def game(gameID, moveNum):
    db = get_db()
    (sessionID, google_account) = sessions.get_session(db,
                                               lambda key: request.cookies.get(key),
                                               None,
                                               ["google_account"])

    # TODO: confirm that the game ID is valid.  Or should this be a function
    #       of the Javascript code???

    return render_template("game.html", sessionID=sessionID, mail=google_account, gameID=gameID)

