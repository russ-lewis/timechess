# The sessions table maps cookies to google accounts.  Sessions can be
# established without a Google account; however, when the user says "log in
# with Google," we go through the OAuth process to figure out their google
# account name.  Note that the google account does not necessarily link the
# user to an account name here on the site; that is done through the Player
# table, which comes next.  But, if the user *has* created a player already,
# then as soon as the session is associated with a google account, the player
# will already be logged in "as" the player.

TABLE: sessions
  INTEGER(64) sessionID  PRIMARY KEY NOT NULL     # randomly selected
  DATETIME    expiration             NOT NULL
  CHAR(128)   google_account

TABLE: oauth_state
  -- TBD --

# Once a person has logged in through OAuth, the session knows their google
# account name.  But until they actually "create" an account on our site,
# that name has no significance.  After they create that account, then the
# process of logging in through OAuth will be (from the user perspective) the
# same thing as "logging into timechess"
#
# While the id# is the underlying ID of the player on the site (although
# never shown to the user) - and thus the ID is the primary key of this table -
# we need to remember that we will *continually* be mapping session IDs to
# player IDs, and then to player names.  So maybe we need to add an index for
# the google_account as well?  Or maybe, we want to have a Redis cache, and
# maybe the Redis cache can contain the player ID and player name, not just
# the google account.  (Or maybe, even *instead of* the google account!)
# Solution TBD.

TABLE: players
  INTEGER     id             PRIMARY KEY NOT NULL AUTO_INCREMENT
  CHAR(128)   google_account             NOT NULL
  CHAR(64)    player_name                NOT NULL       # what people see publicly

# this keeps track of ongoing games.  Later, I'm sure I'll add many fields,
# but for now, it just maps a game ID to the two player IDs involved.
# Note that it does *NOT* (yet) have any information about the end-state of
# the game; if the game ends, we leave the record in this table, and simply
# stop accepting new moves.
 
TABLE: games
  INTEGER id    PRIMARY KEY             NOT NULL AUTO_INCREMENT
  INTEGER white FOREIGN KEY players(id) NOT NULL
  INTEGER black FOREIGN KEY players(id) NOT NULL

# this keeps track of the moves which have happened, over time.  All of the
# moves, from all games, are mixed into a single table.  Each move is
# associated with a gameID, a move number, and a sequence number.  (These
# three fields together are the primary key.)  The game ID is a reference to
# the 'games' table; the move number counts half-moves, with the first
# half-move of white being move 1.  (Thus, the very first move of black -
# their first half-move - is move 2.)  The sequence number is used to record
# changes over time; the very first time that a given half-move number is
# used in a game, it is seq# 1; if it is ever changed, then the old record
# persists, but a new record with seq# 2 is created.
#
# The actual moves are encoded with standard algebraic notation, generally;
# however, we do not support any of the common suffixes, including + or ++.
# Instead, we simply record the move, without comment.  (This is because the
# significance of a move can change, based on edited or invalidated moves,
# earlier in the sequence, and we don't want a single change to trigger many
# row updates.)
#
# We do not record invalidated moves directly; instead, we discover them,
# implicitly, when we try to rebuild the game from the current moves.
#
# In addition to the algebraic notation, the "moves" column can also contain
# various metadata, including:
#   Pass - the player has been passed (they went back in time, and then their
#          opponent appended a new move to the *end* of the history)
#   Pending - the player went back in time, but the opponent has not yet
#             taken another move; this may be converted to Pass, or removed.
#
# Permanent game states, including resignations, draw offers and draw
# accepted, and checkmate are all recorded in the *game* status field (TBD).
#
# The worst-case move is thus:
#      cxd8=Q
# which is 6 characters.  For safety, we set the width to 8 characters.
#
# FINAL NOTE: The debug_seq field is an auto-incrementing counter, which
#             simply exists so that we can re-create changes that happened to
#             the database over time.  Our current design is that all of the
#             records in this database are immutable once created, and if we
#             don't violate that rule with some DELETEs or UPDATEs, we will
#             be able to rebuild the history and recreate old bugs.
#
# UPDATE: I wanted to use AUTO_INCREMENT on debug_seq, but this is not allowed
#         in SQL (the AUTO field must be part of the key).  So we're going to
#         have to set the debug_seq by hand.  I don't know exactly how I want
#         to do that, right now.  If we do this explicitly, with a table
#         search, performance will suck and also we will not be able to handle
#         parallel insertions!  Maybe just turn it into a timestamp?  What
#         sort of time-resolution is possible with those?  Or maybe make this
#         a per-game seqNum???  That would make the search reasonable...
 
TABLE: moves
   # PRIMARY_KEY(gameID,halfMoveNum,seqNum))
   INTEGER    gameID         FOREIGN KEY REFERENCES games(id)
   INTEGER(3) halfMoveNum    NOT NULL
   INTEGER(1) seqNum         NOT NULL
   VARCHAR(8) move           NOT NULL
   INTEGER    debug_seq      NOT NULL AUTO_INCREMENT

