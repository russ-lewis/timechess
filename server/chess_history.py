
import chess   # standard library: python-chess



NOTES:



class Chess_History:
    def __init__(self, history):
        self.board = chess.Board()

        for move in history:
            if move == "pass" or move.startswith("~"):
                self.board.push(chess.Move.null())
            else:
                self.board.push_san(move)

        # NOTE: the board object contains its own history - which is a stack;
        #       I think that we can move backwards through the history, if we
        #       need to do?
        TODO


