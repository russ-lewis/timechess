# this implements the REST api for the timechess site.  It's implemented
# as its own Flask app, independent of the main 'timechess' app (which
# exists to provide the human-visible interface)



import json

from timechess_common import get_db

from flask import Flask, jsonify
app = Flask(__name__)



@app.route("/")
def index():
    return jsonify({"players": url_for("players_get"),
                    "games"  : url_for("games_get"  ),
                    "moves"  : url_for("moves_get"  )})



def build_player_record(p):
    return {"url"  : url_for("one_player", id=p.id),
            "id"   : p.id,
            "name" : p.name,
            "games": url_for("games_by_player", id=p.id)}

@app.route("/players", method="GET")
def players_get():
    db     = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id,username FROM PLAYERS")
    tmp = cursor.fetchall()

    cursor.close()
    db.close()

    retval = [build_player_record(p) for p in tmp]
    return jsonify(retval)



@app.route("/players", method="POST")
def players_post():
    obj = TODO read body of POST
    obj = json.loads(obj)

    # TODO: make this more flexible and adaptible, as we add new fields to
    #       the table.
    if obj.keys() != ["name"]:
        russ_flash("players POST: Invalid input variables.  Variables sent: "+str(obj.keys))
        return redirect(url_for("index"), code=303)

    db     = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT name FROM players WHERE name=%s", (obj.name,))
    if cursor.rowcount != 0:
        russ_flash("players POST: Cannot create new player, name already exists")
        return redirect(url_for("index"), code=303)

    cursor.execute("INSERT INTO players(name) VALUES(%s); SELECT LAST_INSERT_ID();", (obj.name,))
    new_rows = cursor.fetchall()

    cursor.close()
    db.close()

    id = new_row[0][0]
    return redirect(url_for("players", id=id), code=303)



@app.route("/players/<id>", method="GET")
def one_player(id):
    db     = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id,name FROM players WHERE id=%s", (id,))
    rows = cursor.fetchall()

    cursor.close()
    db.close()

    if len(rows) > 1:
        russ_flash("players POST: Internal error: too many rows")
        return redirect(url_for("index"), code=303)

    if len(rows) == 0:
        return render_template("404.html")

    retval = build_player_record(rows[0])
    return jsonify(retval)



def build_game_record(g):
    return {"url"             : url_for("one_game", id=g.id),
            "id"              : g.id,
            "player1_name"    : g.player1_name,
            "player1_url"     : url_for("one_player", id=g.player1_id,
            "player2_name"    : g.player2_name,
            "player2_url"     : url_for("one_player", id=g.player2_id
            "player1_KB_order": g.player1_KB_order,
            "player2_KB_order": g.player2_KB_order}

@app.route("/games", method="GET")
def games_get():
    db     = get_db()
    cursor = db.cursor()

    cursor.execute("""SELECT g.id, p1.id,p1.name, p2.id,p2.name, g.player1_KB_order, g.player2_KB_order
                        FROM games g
                        JOIN players p1 ON p1.id = g.player1
                        JOIN players p2 ON p2.id = g.player2;""")
    tmp = cursor.fetchall()

    cursor.close()
    db.close()

    retval = [build_game_record(g) for g in tmp]
    return jsonify(retval)



@app.route("/players/<id>/games", method="GET")
def games_by_player(id):
    # exactly the same as games_get(), except with a WHERE clause

    db     = get_db()
    cursor = db.cursor()

    cursor.execute("""SELECT g.id, p1.id,p1.name, p2.id,p2.name, g.player1_KB_order, g.player2_KB_order
                        FROM games g
                        JOIN players p1 ON p1.id = g.player1
                        JOIN players p2 ON p2.id = g.player2
                        WHERE p1.id = %s OR p2.id = %s;""", (id,id))
    tmp = cursor.fetchall()

    cursor.close()
    db.close()

    retval = [build_game_record(g) for g in tmp]
    return jsonify(retval)



@app.route("/games", method="POST")
def games_post():
    db     = get_db()
    cursor = db.cursor()

    TODO: implement me



@app.route("/games/<id>", method="GET")
def games_get(id):
    db     = get_db()
    cursor = db.cursor()

    cursor.execute("""SELECT g.id, p1.id,p1.name, p2.id,p2.name, g.player1_KB_order, g.player2_KB_order
                        FROM games g
                        JOIN players p1 ON p1.id = g.player1
                        JOIN players p2 ON p2.id = g.player2
                        WHERE g.id = %s;""", (id,))
    tmp = cursor.fetchall()

    cursor.close()
    db.close()

    retval = [build_game_record(g) for g in tmp]
    return jsonify(retval)



@app.route("/moves", method="GET")
def moves_get():
    TODO implement me



# to return JSON objects: https://blog.miguelgrinberg.com/post/customizing-the-flask-response-class

