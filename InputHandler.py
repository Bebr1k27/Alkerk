from RulesEngine import CAPTURE, MOVE


class InputHandler:
    def __init__(self, player):
        self.player = player

        self.picked = None

    @property
    def pick_options(self):
        if self.picked is None:
            return [m[1] for m in self.player.board.possible_moves]
        else:
            return [(m[2] if len(m) == 3 else m[3]) for m in self.player.board.possible_moves if m[1] == self.picked]

    def on_click(self, x, y):
        if self.picked is None:
            self.picked = None
            if not (x, y) in self.pick_options: return
            self.picked = (x, y)
        else:
            if not (x, y) in self.pick_options:
                self.picked = None
                return
            move = next((m for m in self.player.board.possible_moves if m[1] == self.picked and (m[2] if len(m) == 3 else m[3]) == (x, y)), None)
            status = self.player.commit_move(move)
            if status:
                self.picked = None
            elif move:
                self.picked = move[3] if move[0] == CAPTURE else move[2]
