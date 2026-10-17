from dataclasses import dataclass
from Board import Board, LightBoard, Field, WHITE

inf = 10 ** 27

@dataclass
class Node:
    field: Field
    turn: int
    moves: list
    childs: list[Node]
    value: int | None = None
    preferred_move: list | None = None

def position_cost_0_1(field: Field) -> int:
    return field.white_count() - field.black_count()

class Model:
    def __init__(self, side: int, board: Board, depth: int = 5):
        self.side = side
        self.depth = depth

        self.game_board = board
        self.virtual_board = LightBoard(self.game_board.field.size)

        self._modifier = 1 if self.side == WHITE else -1

    def minimax(self, node: Node, deep: int, a: int, b: int, maximazingPlayer: bool):
        if not node.value: node.value = position_cost_0_1(node.field) * self._modifier
        if deep == 0: return node.value
        if not node.moves:
            node.moves = self.virtual_board.possible_moves
        if not node.moves: return node.value
        if maximazingPlayer:
            value = -inf
            for move in node.moves:
                self.virtual_board.commit_move(move)
                child = Node(self.virtual_board.field.copy(), self.virtual_board.move, [], [])
                node.childs.append(child)
                vl = self.minimax(child, deep - 1, a, b, not maximazingPlayer)
                self.virtual_board.revert_move(move)
                if vl > value:
                    value = vl
                    node.preferred_move = move
                if value >= b: break
                a = max(a, value)
            # node.value = value
            return value
        else:
            value = inf
            for move in node.moves:
                before = self.virtual_board.field.hash
                self.virtual_board.commit_move(move)
                child = Node(self.virtual_board.field.copy(), self.virtual_board.move, [], [])
                node.childs.append(child)
                vl = self.minimax(child, deep - 1, a, b, not maximazingPlayer)
                self.virtual_board.revert_move(move)
                if vl < value:
                    value = vl
                    node.preferred_move = move
                if value <= a: break
                b = min(b, value)
            # node.value = value
            return value

    def find_move(self):
        root = Node(self.game_board.field, self.game_board.move, [], [])
        self.virtual_board.load_position(root.field, root.turn)
        self.minimax(root, self.depth, -inf, inf, True)
        print(f"Preferred move: {root.preferred_move}, Value: {root.value}")
        return LightBoard._unformat_capture_move(root.preferred_move)