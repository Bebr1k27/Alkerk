import pygame
from Board import Board, WHITE, BLACK, MOVE, CAPTURE
from InputHandler import InputHandler
from SETTINGS import *
from dataclasses import dataclass
from Game import Game
from Player import Player

from ai import Model

@dataclass
class Highlight:
    x: int
    y: int
    color: tuple | str
    radius: int = ROCK_RADIUS + 10
    width: int = 10

class Visualizer:
    def __init__(self, game: Game, screen: pygame.Surface):
        self.game = game
        self.screen = screen
        self.highlights = []
        self.input_handlers = [(InputHandler(player) if player.needs_input else None) if player else None for player in game.players]
        # self.input_handler = InputHandler(self.game.board)

        self.set_highlights()

        self.clock = pygame.time.Clock()
        self.last_turn = self.turn

    @property
    def turn(self):
        return 1 if self.game.board.move == WHITE else 0

    def rect(self, x1: int, y1: int, x2: int, y2: int, color: tuple | str, width: int = 0):
        pygame.draw.rect(self.screen, color, (x1, y1, x2 - x1, y2 - y1), width)

    def circled_rect(self, x1: int, y1: int, x2: int, y2: int, color: tuple | str, radius: int = 0, width: int = 0):
        self.rect(x1, y1 + radius, x2, y2 - radius, color)
        self.rect(x1 + radius, y1, x2 - radius, y2, color)
        pygame.draw.circle(self.screen, color, (x1 + radius, y1 + radius), radius, width)
        pygame.draw.circle(self.screen, color, (x2 - radius, y1 + radius), radius, width)
        pygame.draw.circle(self.screen, color, (x1 + radius, y2 - radius), radius, width)
        pygame.draw.circle(self.screen, color, (x2 - radius, y2 - radius), radius, width)

    def rock(self, x: int, y: int, team: int):
        color = BLUE if team == WHITE else RED
        w, h = self.screen.get_size()
        BOARD_SIZE = (self.game.board.field.size - 1) * CELL
        pygame.draw.circle(self.screen, color, ((w - BOARD_SIZE) // 2 + x * CELL + LINE_WIDTH // 2, (h - BOARD_SIZE) // 2 + y * CELL + LINE_WIDTH // 2), ROCK_RADIUS)
        pygame.draw.circle(self.screen, LINE_COLOR, ((w - BOARD_SIZE) // 2 + x * CELL + LINE_WIDTH // 2, (h - BOARD_SIZE) // 2 + y * CELL + LINE_WIDTH // 2), ROCK_RADIUS, LINE_WIDTH)
        pygame.draw.circle(self.screen, LINE_COLOR, ((w - BOARD_SIZE) // 2 + x * CELL + LINE_WIDTH // 2, (h - BOARD_SIZE) // 2 + y * CELL + LINE_WIDTH // 2), ROCK_RADIUS * 0.8, LINE_WIDTH)

    def draw(self):
        self.screen.fill(BG_COLOR)
        BOARD_SIZE = (self.game.board.field.size - 1) * CELL
        DESK_SIZE = BOARD_SIZE + BORDER * 2 + DESK_PADDING * 2
        w, h = self.screen.get_size()
        self.circled_rect((w - DESK_SIZE) // 2, (h - DESK_SIZE) // 2, (w + DESK_SIZE) // 2, (h + DESK_SIZE) // 2, DESK_COLOR, radius=CELL // 2)  # Desk
        self.rect((w - BOARD_SIZE) // 2, (h - BOARD_SIZE) // 2, (w + BOARD_SIZE) // 2, (h + BOARD_SIZE) // 2, BOARD_COLOR)                       # Board

        for i in range(self.game.board.field.size):  # Ortogonal lines
            pygame.draw.line(self.screen, LINE_COLOR, ((w - BOARD_SIZE) // 2, (h - BOARD_SIZE) // 2 + i * CELL), ((w + BOARD_SIZE) // 2, (h - BOARD_SIZE) // 2 + i * CELL), LINE_WIDTH)
            pygame.draw.line(self.screen, LINE_COLOR, ((w - BOARD_SIZE) // 2 + i * CELL, (h - BOARD_SIZE) // 2), ((w - BOARD_SIZE) // 2 + i * CELL, (h + BOARD_SIZE) // 2), LINE_WIDTH)

        for i in range(0, self.game.board.field.size, 2):  # Diagonal lines
            pygame.draw.line(self.screen, LINE_COLOR, ((w - BOARD_SIZE) // 2 + i * CELL, (h - BOARD_SIZE) // 2), ((w - BOARD_SIZE) // 2, (h - BOARD_SIZE) // 2 + i * CELL), LINE_WIDTH)
            pygame.draw.line(self.screen, LINE_COLOR, ((w + BOARD_SIZE) // 2 - i * CELL, (h - BOARD_SIZE) // 2), ((w + BOARD_SIZE) // 2, (h - BOARD_SIZE) // 2 + i * CELL), LINE_WIDTH)
            pygame.draw.line(self.screen, LINE_COLOR, ((w - BOARD_SIZE) // 2 + i * CELL, (h + BOARD_SIZE) // 2), ((w - BOARD_SIZE) // 2, (h + BOARD_SIZE) // 2 - i * CELL), LINE_WIDTH)
            pygame.draw.line(self.screen, LINE_COLOR, ((w + BOARD_SIZE) // 2 - i * CELL, (h + BOARD_SIZE) // 2), ((w + BOARD_SIZE) // 2, (h + BOARD_SIZE) // 2 - i * CELL), LINE_WIDTH)

        for y in range(self.game.board.field.size):
            for x in range(self.game.board.field.size):
                r = 3 if x == y == self.game.board.field.size // 2 else (2 if x % 2 == y % 2 else 1)
                pygame.draw.circle(self.screen, LINE_COLOR, ((w - BOARD_SIZE) // 2 + x * CELL + LINE_WIDTH // 2, (h - BOARD_SIZE) // 2 + y * CELL + LINE_WIDTH // 2), DECO_RADIUS * r, LINE_WIDTH)
        
        self.rect((w - BOARD_SIZE) // 2 - BORDER, (h - BOARD_SIZE) // 2 - BORDER, (w + BOARD_SIZE) // 2 + BORDER + LINE_WIDTH, (h + BOARD_SIZE) // 2 + BORDER + LINE_WIDTH, BORDER_COLOR, width=BORDER)  # Border

        for y in range(self.game.board.field.size):            # Rocks
            for x in range(self.game.board.field.size):
                if self.game.board.field.grid(x, y) != 0:
                    self.rock(x, y, self.game.board.field.grid(x, y))

        for i in self.highlights:
            pygame.draw.circle(self.screen, i.color, ((w - BOARD_SIZE) // 2 + i.x * CELL + LINE_WIDTH // 2, (h - BOARD_SIZE) // 2 + i.y * CELL + LINE_WIDTH // 2), i.radius, i.width)

    def _hightlight_consequences(self, move):
        for i in move[4]:
            self.highlights.append(Highlight(i[2][0], i[2][1], "#FF0000", width=5, radius=ROCK_RADIUS + 5))
            self.highlights.append(Highlight(i[3][0], i[3][1], "#00DDFF", width=5, radius=10))
            if i[4]: self._hightlight_consequences(i)

    def set_highlights(self):
        if self.game.players[self.turn] is None:
            self.highlights.clear()
            return
        if not self.game.players[self.turn].needs_input:
            self.highlights.clear()
            return
        input_handler = self.input_handlers[self.turn]
        self.highlights.clear()
        if input_handler.picked is None:
            for move in self.game.board.possible_moves:
                self.highlights.append(Highlight(move[1][0], move[1][1], (0, 255, 0), width=5))
        else:
            self.highlights.append(Highlight(input_handler.picked[0], input_handler.picked[1], (0, 255, 0)))
            for move in [i for i in self.game.board.possible_moves if i[1] == input_handler.picked]:
                if move[0] == MOVE:
                    self.highlights.append(Highlight(move[2][0], move[2][1], "#00DDFF", width=5, radius=20))
                elif move[0] == CAPTURE:
                    self.highlights.append(Highlight(move[2][0], move[2][1], "#FF0000", width=5))
                    self.highlights.append(Highlight(move[3][0], move[3][1], "#00DDFF", width=5, radius=20))
                    self._hightlight_consequences(move)

    def handle_click(self, pos):
        if self.game.players[self.turn] is None: return
        if not self.game.players[self.turn].needs_input: return
        w, h = self.screen.get_size()
        BOARD_SIZE = (self.game.board.field.size - 1) * CELL
        x, y = pos[0] - (w - BOARD_SIZE - CELL) // 2, pos[1] - (h - BOARD_SIZE - CELL) // 2
        if not 0 <= x < BOARD_SIZE + CELL > y >= 0: return
        x, y = x // CELL, y // CELL
        self.input_handlers[self.turn].on_click(x, y)
        self.set_highlights()

    def update(self):
        if self.last_turn != self.game.board.move:
            ...
        self.last_turn = self.game.board.move

        if self.game.players[self.turn] and not self.game.players[self.turn].needs_input:
            status = self.game.players[self.turn].make_decision()
            if not status:
                print("!!!")
            self.set_highlights()

    def live_cycle(self):
        while True:
            self.clock.tick(FPS_LIMIT)
            for i in pygame.event.get():
                if i.type == pygame.QUIT:
                    return
                if i.type == pygame.MOUSEBUTTONDOWN and i.button == 1:
                    self.handle_click(i.pos)
            self.update()
            self.draw()
            pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    game = Game(7)
    game.add_player(WHITE, "WHITE PLAYER", True)
    # game.add_ai(WHITE, Model(WHITE, game.board, depth=9), "WHITE AI")
    game.add_ai(BLACK, Model(BLACK, game.board, depth=5), "BLACK AI")
    # game.add_player(BLACK, "BLACK PLAYER", True)
    visualizer = Visualizer(game, screen)
    game.start_game()
    visualizer.live_cycle()
