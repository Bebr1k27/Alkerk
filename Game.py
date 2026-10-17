from Board import Board, WHITE, BLACK
from Player import Player, AI_Player, Model

class Game:
    def __init__(self, size: int):
        self.board = Board(size)
        self.players: list[Player | None] = [None, None]

    def add_player(self, side: int, name: str = "Unknown", needs_input: bool = True):
        if side == WHITE: index = 1
        elif side == BLACK: index = 0
        else: raise Exception(f"Invalid player side: {side}")
        if self.players[index]: raise Exception("That player already exists")
        self.players[index] = Player(side, self.board, name, needs_input)

    def add_ai(self, side: int, model: Model, name: str = "Unknown"):
        if side == WHITE: index = 1
        elif side == BLACK: index = 0
        else: raise Exception(f"Invalid player side: {side}")
        if self.players[index]: raise Exception("That player already exists")
        self.players[index] = AI_Player(model, side, self.board, name)

    def start_game(self):
        self.board.start_game()