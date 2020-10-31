
import chess   # standard library: python-chess



class TimeChess_Game:
    """Models the history of a TimeChess game; it has a sequence of moves
       (some of which are invalidated, or are "pass").  It keeps a chess.Board
       object inside it, which represents the state of the board at the end of
       the sequence; you can add new moves to the history (finding out, as you
       go, which need to be invalidated).
    """

    def __init__(self):
        self.board = chess.Board()

    def add_to_history(self, move):
        """Takes a move, and tries to apply it.  Give the old version of the
           move (including the invalidation mark) if necessary.  Returns the
           new version of the move (as a string) IF IT CHANGES.  Returns None
           otherwise.
        """

        # the caller must check for this!
        assert not self.board.is_game_over()

        if move == "Pass":
            self.board.push(chess.Move.null())
            return None

        if move == "WhRes":
            TODO
        if move == "BlRes":
            TODO
        if move == "Draw":
            TODO

        if move[0] == '~':
            base_move = move[1:]
        else:
            base_move = move

        # attempt the move.  If it's not valid in the current configuration, then
        # a ValueError will be thrown; in that case, push a null move instead.  In
        # either case, record the new_move as the result: either base_move, or an
        # invalidated version of it.

        try:
            self.board.push_san(base_move)
            # if we get here, the move succeeded!
            new_move = base_move
        except ValueError:
            # if we get here, the move was illegal.
            new_move = '~'+base_move

        # should the caller update the database?  We tell them by either returning
        # None (no change), or the updated move string.
        if new_move == move:
            return None
        else:
            return new_move

    def is_game_over(self):
        return self.board.is_game_over()

    def legal_moves_san(self):
        return [self.board.san(m) for m in self.board.legal_moves]

    def piece_list_xy(self):
        piece_map = self.board.piece_map()
        retval = []
        for sq in piece_map:
            x =   chess.square_file(sq)
            y = 7-chess.square_rank(sq)
            retval.append( (x,y, piece_map[sq].symbol()) )
        return retval

    def get_simple_drawing(self):
        return str(self.board)


