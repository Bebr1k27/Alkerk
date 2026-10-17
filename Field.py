from functools import lru_cache

WHITE = 3
BLACK = 5
EMPTY = 0

class Field:
    def __init__(self, size, white=0, black=0):
        self.size = size
        self.cells = size * size

        self._empty = 0
        self._all_cells = (1 << self.cells) - 1

        self._white = white  # Bitmap of white pieces
        self._black = black  # Bitmap of black pieces
        self._neighbors = self._build_neighbors()  # Bitmap of neighbors for all the cells

    def copy(self): return Field(self.size, self._white, self._black)

    def _build_neighbors(self):
        neighbors = [0] * self.cells
        for y in range(self.size):
            for x in range(self.size):
                square = y * self.size + x
                dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                if x % 2 == y % 2:
                    dirs += [(1, 1), (-1, -1), (1, -1), (-1, 1)]
                mask = 0
                for dx, dy in dirs:
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        mask |= 1 << (ny * self.size + nx)
                neighbors[square] = mask
        return neighbors

    def reset(self) -> None:
        self._white = (1 << self.cells // 2) - 1
        self._black = ((1 << self.cells // 2) - 1) << (self.cells // 2 + 1)

    def _pos(self, x, y): return self.cells - self.size * y - x - 1
    def _is_white(self, x): return (self._white & (1 << x)) >> x
    def _is_black(self, x): return (self._black & (1 << x)) >> x
    def _color(self, x): return WHITE * self._is_white(x) + BLACK * self._is_black(x)

    def white_count(self): return self._white.bit_count()
    def black_count(self): return self._black.bit_count()

    @property
    def _occupied(self): return self._white | self._black

    @property
    def _free(self): return self._all_cells ^ self._occupied

    def grid(self, x, y): return self._color(self._pos(x, y))
    def grid_set(self, x, y, value):
        pos = self._pos(x, y)
        if value == WHITE: self._white |= 1 << pos
        elif value == BLACK: self._black |= 1 << pos
        else:
            mask = (self._all_cells >> (pos + 1) << (pos + 1)) + (1 << pos) - 1
            self._white &= mask
            self._black &= mask

    @staticmethod
    @lru_cache()
    def _moves_for_ceil(size, x, y) -> list[tuple[int, int]]:
        moves = []
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if x % 2 == y % 2:
            dirs += [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size:
                moves.append((nx, ny))
        return moves

    def moves_for_ceil(self, x, y) -> list[tuple[int, int]]:
        return self._moves_for_ceil(self.size, x, y)

    @property
    def hash(self):
        ans = 0
        mod = 10 ** 9 + 13
        pw = 1
        for i in range(self.cells):
            ans = (ans + self._color(i) * pw) % mod
            pw *= 2
        return ans


if __name__ == "__main__":
    test = Field(5)
    test.reset()
    print(format(test._white, 'b'))
    print(format(test._black, 'b'))
    print(format(test._occupied, 'b'))
    print(format(test._free, 'b'))
    test.grid_set(0, 0, 0)
    for i in range(0, test.size):
        for k in range(0, test.size):
            print(test._color(test._pos(k, i)), end=" ")
        print()
    print(test.white_count(), test.black_count())
