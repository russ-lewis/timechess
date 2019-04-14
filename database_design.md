The main game database will need to store a little bit of common game state, plus
a move history for each game.

TABLE: players
  INTEGER     id       PRIMARY KEY NOT NULL AUTO_INCREMENT
  VARCHAR(64) username NOT NULL

TABLE: games
  INTEGER id      PRIMARY KEY NOT NULL AUTO_INCREMENT
  INTEGER player1 FOREIGN KEY (players.id) NOT NULL
  INTEGER player2 FOREIGN KEY (players.id) NOT NULL
  VARCHAR(2) player1_KB_order
  VARCHAR(2) player2_KB_order
 
 TABLE: moves
   # PRIMARY_KEY(gameID,num,color)
   INTEGER    gameID FOREIGN KEY (games.id)
   INTEGER(3) num    NOT NULL
   CHAR       color  NOT NULL
   VARCHAR(5) move   NOT NULL   # use standard encoding.  Worst case: Naxb3,0-0-0  Special cases: WhRes BlRes Draw
