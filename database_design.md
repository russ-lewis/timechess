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
   VARCHAR(5) move   NOT NULL   # use standard encoding.  Worst case: Naxb3,0-0-0  Special cases: WhRes BlRes Draw.  No "notes", such as "+" (for Check), "e.p.", or commentary.
