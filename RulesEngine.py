from Field import Field, WHITE, BLACK, EMPTY

MOVE = "MOVE"
CAPTURE = "CAPTURE"

class RulesEngine:
    @staticmethod
    def _move(field: Field, x: int, y: int) -> list[tuple[int, int]]:
        moves = field.moves_for_ceil(x, y)
        possible_moves = []
        color = field.grid(x, y)
        banned = 1 if color == WHITE else -1

        for move in moves:
            nx, ny = move[0], move[1]
            if not 0 <= nx < field.size > ny >= 0: continue
            if field.grid(nx, ny) != EMPTY: continue
            if ny - y == banned: continue # Can't move backwards
            possible_moves.append([MOVE, (x, y), (nx, ny)])
    
        return possible_moves

    @staticmethod
    def _capture(field: Field, x: int, y: int, taken: set[tuple[int, int]], orig_color: int | None = None) -> list[tuple[int, int]]:
        moves = field.moves_for_ceil(x, y)
        color = field.grid(x, y) if orig_color is None else orig_color
        opposite = WHITE + BLACK - color
        possible_moves = []

        for move in moves:
            vx, vy = move[0] - x, move[1] - y # Vector from current position to neighbor
            tx, ty =  x + vx, y + vy          # Capture target
            dx, dy =  x + vx * 2, y + vy * 2  # Destiny ceil
            if not 0 <= dx < field.size > dy >= 0: continue
            if not field.grid(tx, ty) == opposite: continue
            if field.grid(dx, dy) != EMPTY: continue
            if (tx, ty) in taken: continue

            ans = RulesEngine._capture(field, dx, dy, taken | {(tx, ty)}, color)
            possible_moves.append([CAPTURE, (x, y), (tx, ty), (dx, dy), ans])

        return possible_moves

    @staticmethod
    def get_possible_moves(field: Field, x: int, y: int) -> list[tuple[int, int]]:       
        # possible_moves = RulesEngine._move(field, x, y) # Move
        # possible_moves.extend(RulesEngine._capture(field, x, y, set())) # Capture
        possible_moves = RulesEngine._capture(field, x, y, set()) # Capture
        if not possible_moves: # If no capture moves, allow normal moves
            possible_moves = RulesEngine._move(field, x, y) # Move
        return possible_moves
