import pygame
from engine import *

size = WIDTH, HEIGHT = 768, 768
FPS = 15

DIM = 8 # 8x8 board

WHITE = 255, 255, 255
GRAY = 100, 100, 100
BLACK = 0, 0, 0

PURPLE = 136, 121, 181
SOFT_WHITE = 239, 239, 239

NAVY_BLUE = 77, 116, 152
BEIGE_WHITE = 234, 233, 211

RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255

LIGHT_COLOR = SOFT_WHITE
DARK_COLOR = PURPLE

SQ_SIZE = int(WIDTH / DIM) # 768/8 = 96
HIGHLIGHT_THICKNESS = 4
BUTTON_COLOR = BLACK

class Game:

    def __init__(self, title: str, size:tuple[int, int]):
        pygame.init()
        pygame.display.set_caption(title)
        self.screen = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()
        self.running = True
        self.highlighted = None
        self.buttons = None

        self.state = GameState()
        self.pieces = ['wP', 'bP', 'wK', 'bK', 'wQ', 'bQ', 'wB', 'bB', 'wN', 'bN', 'wR', 'bR']

    def new(self):
        self.square_selected = ()
        self.clicks = []
        self.load_images()
        self.state.create_start_pos()
        self.run()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.draw()
            pygame.display.flip()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                col = (pos[0] // SQ_SIZE)
                row = (pos[1] // SQ_SIZE)
                if self.square_selected == (row, col): # If same square is selected twice
                    self.square_selected = ()
                    self.clicks = []
                    self.highlighted = None
                else:
                    self.square_selected = row, col
                    self.clicks.append(self.square_selected)
                    if len(self.clicks) == 2: # if the self.clicks licks is 2 long
                        self.successful_move()
                    else: # First click, check if the piece is of the correct color, if not clears the click log
                        piece = self.state.board[self.clicks[0][0]][self.clicks[0][1]]
                        if self.state.check_player_move(piece):
                            pos = self.clicks[0]
                            self.highlight_piece(pos)
                        else:
                            self.clicks = []

    def successful_move(self):
        start_square = self.clicks[0][0], self.clicks[0][1]
        end_square = self.clicks[1][0], self.clicks[1][1]
        move = Move(start_square, end_square, self.state.board)
        if move.is_move_legal(self.moves): # if the move is legal
            self.state.move_list.append(move.notation)
            move.check_enpassant(self.state.white_to_move, self.state.move_list, self.state.board)
            move.move_piece()
            promotion = self.state.check_promotion(end_square)
            if promotion:
                self.promote(end_square)
            self.clicks = []
            self.highlighted = None
            self.state.white_to_move = not self.state.white_to_move
        else:
            self.clicks = []
            self.highlighted = None
        print(self.state.move_list)

    def highlight_piece(self, pos:tuple):
        row, col = pos
        box = [col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE]
        self.moves = self.state.all_legal_moves()
        self.highlighted = box

    def check_highlighted_piece(self):
        if self.highlighted != None:
            pygame.draw.rect(self.screen, RED, self.highlighted, HIGHLIGHT_THICKNESS)

    def load_images(self):
        self.images = {}
        for piece in self.pieces:
            self.images[piece] = pygame.transform.scale(pygame.image.load(f"Images/{piece}.png"), (SQ_SIZE, SQ_SIZE))

    def promote(self, pos:tuple[int, int]):
        piece = self.state.board[pos[0]][pos[1]]
        to_promote = "Q"
        self.state.board[pos[0]][pos[1]] = piece[0] + to_promote


    def draw(self):
        self.screen.fill(WHITE)

        self.draw_board()
        self.draw_pieces()
        self.check_highlighted_piece()

    def draw_board(self):
        colors = [LIGHT_COLOR, DARK_COLOR]

        for r in range(DIM):
            for c in range(DIM):
                color = colors[(r + c) % 2]
                pygame.draw.rect(self.screen, color, pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

    def draw_pieces(self):
        for r in range(DIM):
            for c in range(DIM):
                piece = self.state.board[r][c]
                if piece != ' ':
                    self.screen.blit(self.images[piece], (SQ_SIZE*c, SQ_SIZE*r))

def main():
    game = Game("Chess", size)
    game.new()

if __name__ == "__main__":
    main()
