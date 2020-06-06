The main game database will need to store a little bit of common game state, plus
a move history for each game.

TABLE: games
  INTEGER id    PRIMARY KEY              NOT NULL AUTO_INCREMENT
  INTEGER white FOREIGN KEY (players.id) NOT NULL
  INTEGER black FOREIGN KEY (players.id) NOT NULL
 
TABLE: moves
   # PRIMARY_KEY(gameID,num,color)
   INTEGER    gameID FOREIGN KEY (games.id)
   INTEGER(3) num    NOT NULL
   CHAR       color  NOT NULL
   VARCHAR(7) move   NOT NULL   # use standard encoding (except that you can *PREFIX* with ~ to indicate an invalidated move).  Worst case: cxd8=Q  Special cases: WhRes BlRes Draw.  No "notes", such as "+" (for Check), "e.p.", or commentary.



TABLE: log
    # probably a transient table, but useful for debugging; instead of
    # storing the *current* state of each game, it instead stores the list of
    # *changes* over time for each game, so that we can rebuild the history
    # needed.  NOTE: It does *not* record invalidations, just user actions;
    # since invalidations can be rebuilt as-needed from the history

    INTEGER    id     PRIMARY KEY NOT NULL AUTO_INCREMENT
    INTEGER    gameID FOREIGN KEY (games.id)
    INTEGER(3) num    NOT NULL
    CHAR       color  NOT NULL
    VARCHAR(6) move   NOT NULL
    

