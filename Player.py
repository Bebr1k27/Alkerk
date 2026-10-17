from Board import Board
from ai import Model


class Player:
    def __init__(self, side: int, board: Board, name: str = "Unknown", needs_input: bool = True):
        self.side = side
        self.board = board

        self.name = name
        self.needs_input = needs_input

    def commit_move(self, move, flag=False):
        return self.board.commit_move(move, flag)

class AI_Player(Player):
    def __init__(self, model: Model, side: int, board: Board, name: str = "Unknown"):
        super().__init__(side, board, name, False)
        self.model = model

    def make_decision(self):
        move = self.model.find_move()
        if move:
            return self.commit_move(move, flag=True)
        return False
