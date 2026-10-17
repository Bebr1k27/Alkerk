from Field import Field, WHITE, BLACK, EMPTY
from RulesEngine import RulesEngine, MOVE, CAPTURE

class Board:
    def __init__(self, size: int):
        self.field = Field(size)
        self.move = WHITE

        self.free = True
        self.moves = []

        self.history = []

    def start_game(self):
        self.field.reset()
        self.move = WHITE
        self.free = True
        self.moves = []

    def end_move(self):
        self.move = WHITE if self.move == BLACK else BLACK
        self.free = True
        self.moves = []

    @property
    def possible_moves(self) -> list[list]:
        if self.free:
            moves = []
            flag = False
            for y in range(self.field.size):
                for x in range(self.field.size):
                    if self.field.grid(x, y) == self.move:
                        new_moves = RulesEngine.get_possible_moves(self.field, x, y)
                        for i in new_moves:
                            flag = flag or i[0] == CAPTURE
                        moves.extend(new_moves)
            if flag:
                moves = [i for i in moves if i[0] == CAPTURE]
            return moves
        else:
            return self.moves

    def commit_move(self, move, enable_chain_capture=False):
        if move[0] == MOVE:
            pos_from = move[1]
            pos_to = move[2]
            color = self.field.grid(*pos_from)
            self.field.grid_set(pos_from[0], pos_from[1], EMPTY)
            self.field.grid_set(pos_to[0], pos_to[1], color)
            self.end_move(move)
            return True
        elif move[0] == CAPTURE:
            pos_from = move[1]
            pos_capture = move[2]
            pos_to = move[3]
            consequences = move[4]
            color = self.field.grid(*pos_from)
            if enable_chain_capture:
                    while move:
                        self.field.grid_set(move[1][0], move[1][1], EMPTY)
                        self.field.grid_set(move[2][0], move[2][1], EMPTY)
                        self.field.grid_set(move[3][0], move[3][1], color)
                        move = move[4]
                    self.end_move()
                    return True
            else:
                self.field.grid_set(pos_from[0], pos_from[1], EMPTY)
                self.field.grid_set(pos_capture[0], pos_capture[1], EMPTY)
                self.field.grid_set(pos_to[0], pos_to[1], color)
                if consequences:
                    self.free = False
                    self.moves = consequences
                    return False
                else:
                    self.end_move()
                    return True
        else:
            raise ValueError("Invalid move type")

class LightBoard:
    def __init__(self, size: int) -> None:
        self.field = Field(size)
        self.move = WHITE

    def load_position(self, field, turn):
        self.field = field
        self.move = turn

    def end_move(self): self.move = WHITE + BLACK - self.move

    @staticmethod
    def _format_capture_move(move):
        if not move[4]: return [[move[0], move[1], [move[2]], move[3]]]
        out = []
        for i in move[4]:
            moves = LightBoard._format_capture_move(i)
            for k in moves:
                out.append([move[0], move[1], [move[2]] + k[2], k[3]])
        return out

    @staticmethod
    def _unformat_capture_move(move):
        if move is None: return move
        if move[0] == MOVE: return move
        takes = move[2]
        final_pos = move[3]
        start_pos = move[1]
        result = [CAPTURE, move[1], takes[0], None, []]
        current = result
        for i in range(1, len(takes)):
            vector = (takes[i - 1][0] - start_pos[0], takes[i - 1][1] - start_pos[1])
            current[3] = (takes[i - 1][0] + vector[0], takes[i - 1][1] + vector[1])
            start_pos = current[3]
            current[4] = [CAPTURE, current[3], takes[i], None, []]
            current = current[4]
        current[3] = final_pos
        return result

    @property
    def possible_moves(self):
        moves = []
        flag = False
        for y in range(self.field.size):
            for x in range(self.field.size):
                if self.field.grid(x, y) == self.move:
                    new_moves = RulesEngine.get_possible_moves(self.field, x, y)
                    for i in new_moves:
                        flag = flag or i[0] == CAPTURE
                    moves.extend(new_moves)
        if flag:
            out = []
            for i in moves:
                if i and i[0] == MOVE: continue
                out.extend(self._format_capture_move(i))
            moves = out
        return moves

    def commit_move(self, move):
        if move[0] == MOVE:
            pos_from = move[1]
            pos_to = move[2]
            color = self.field.grid(*pos_from)
            self.field.grid_set(pos_from[0], pos_from[1], EMPTY)
            self.field.grid_set(pos_to[0], pos_to[1], color)
            self.end_move()
            return True
        elif move[0] == CAPTURE:
            pos_from = move[1]
            pos_capture = move[2]
            pos_to = move[3]
            color = self.field.grid(*pos_from)
            self.field.grid_set(pos_from[0], pos_from[1], EMPTY)
            for pos in pos_capture:
                self.field.grid_set(pos[0], pos[1], EMPTY)
            self.field.grid_set(pos_to[0], pos_to[1], color)
            self.end_move()
            return True
        else:
            raise ValueError("Invalid move type")

    def revert_move(self, move):
        if move[0] == MOVE:
            pos_from = move[1]
            pos_to = move[2]
            color = self.field.grid(*pos_to)
            self.field.grid_set(pos_from[0], pos_from[1], color)
            self.field.grid_set(pos_to[0], pos_to[1], EMPTY)
            self.end_move()
            return True
        elif move[0] == CAPTURE:
            pos_from = move[1]
            pos_capture = move[2]
            pos_to = move[3]
            color = self.field.grid(*pos_to)
            opposite = WHITE + BLACK - color
            self.field.grid_set(pos_from[0], pos_from[1], color)
            for pos in pos_capture:
                self.field.grid_set(pos[0], pos[1], opposite)
            self.field.grid_set(pos_to[0], pos_to[1], EMPTY)
            self.end_move()
            return True
        else:
            raise ValueError("Invalid move type")
