# timechess
A web-based implementation of "Time Traveling Chess"

This website is based off of Flask, Python 2.x, and MySQL; I'm currently deploying it on EC2.

# What is Time Traveling Chess?

Time Traveling Chess is ordinary chess, except that, for any one of your moves, you have the
option of *changing* a previous move, instead of making a new one.  Any time that you change
a move, you must *upgrade* which piece is moving - that is, you must move a more valuable
piece.  The order of value, in increasing order, is:
   Pawn -> Knight/Bishop -> Rook -> Queen -> King.
Thus, you can replace a Pawn move with a Rook move, but it is illegal to replace a Queen move
with a Bishop move.

(Since there is some debay whether Knights or Bishops are more valuable, the game actually
allows the player to choose.  Basically, the first time in a game that a player replaces a
Knight move with a Bishop move (or vice-versa), the game records that as the player's
implicit ordering preference (for this game).  For the rest of the game, the ordering must
be respected.)

When a player replaces an old move, this can invalidate other moves, which happened later in
the game.  For instance, if the piece was later captured, then the capture is invalidated.
Or, perhaps the piece now makes it *impossible* to make some move which happens later, because
it blocks the way - or, it may make a non-capture move invalid because it would now be a
capture.  Finally, the move may make some moves illegal - perhaps by causing Check which was
not previously present, or making a Castle move invalid.

To find the invalid moves, we rebuild the game state, attempting to make each move exactly as
recorded in the past.  If a move is invalid, then that move is deleted from the history, but
the other moves that follow it are *NOT REMOVED* - instead, we temporarily treat the move as
a NOP or "pass".  This is, of course, not a legal chess move, but we allow it temporarily,
until it is filled in later.

In the future, a player who has had moves invalidated may use one of their moves to fill in
an invalidated move; this takes a turn, just like all other moves.

At no time may a player create a new move (at the end of the game history, replacing an old
one, or filling in a blank space in the middle) which is illegal according to the current
game history.  Thus, it is illegal to move in such a way that leaves you in Check at the end
of your move.

However, it is perfectly legal to allow a Check to remain in the history, unresolved (potentially
for many moves!) through arbitrarily many turns, so long as none of the new moves that you create
perpetuate that state.  Likewise, Checkmate is not actually Checkmate in a final sense, so long
as there is a possibility that the history which lead up to it might change.

Thus, if Checkmate occurs at some point in the history (note that, due to move changes or
invalidations, it's possible to arrive at Checkmate in the *middle* of the history!), the game
is not lost so long as one (or both) of the following conditions are still true:
  * The "winner" has one or more blank moves which still need to be filled in
  * The "loser" has one or more blank moves *or* upgradable moves

Note that it is permissible for the game to end when the "winner" has upgradable moves; they are
permitted to "accept" an end to the game by declining to upgrade any of the moves that lead to
the game end.

(The same is true for Stalemate - although in this case, for the game to end, then *BOTH* players
have to either have no upgradeable moves, or be willing to accept the end of game.)

Note that if a player chooses to "accept" the game end as it stands - which is only a legal action
if that player has no blank moves up to a terminal state - then that player makes no moves that
turn.

TODO: Should this be a permanent state, at least until the terminus changes?  It would be handy
to make it permanent - but then, it might be possible for the "loser" to make dramatic changes to
the game state before eventually "unlocking" it.  Is that a realistic problem?

Finally, note that a player may Resign (or suggest a Draw) at any time.
