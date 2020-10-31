
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
        """Takes a move, and tries to apply it.  If the move works, then
           return True; otherwise, push a null move, and return False.
           Note that if the move was "Pass", then we push the null move, but
           then return True (because we successfully pushed the requested
           move).
        """

        # the caller must check for this!
        assert not self.board.is_game_over()

        if move == "Pass":
            self.board.push(chess.Move.null())
            return True

        # attempt the move.  If it's not valid in the current configuration,
        # then a ValueError will be thrown; in that case, push a null move
        # instead.

        try:
            self.board.push_san(move)
            # if we get here, the move succeeded!
            return True

        except ValueError:
            # if we get here, the move was illegal.
            self.board.push(chess.Move.null())
            return False

    def apply_move(self, move):
        # the caller must confirm that this is legal before this happens!
        self.board.push_san(move)



    def is_game_over(self):
        return self.board.is_game_over()

    def legal_moves_san(self):
        return [self.board.san(m) for m in self.board.legal_moves]

    def move_is_legal(self, move):
        # TODO: Fix terrible design, convert 'move' to the form used by legal_moves, then check more directly
        return move in self.legal_moves_san()

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


