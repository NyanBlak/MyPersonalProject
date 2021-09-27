import pygame
from engine import GameState

size = WIDTH, HEIGHT = 768, 768
FPS = 15

DIM = 8 # 8x8 board

WHITE = 255, 255, 255
GRAY = 100, 100, 100
BLACK = 0, 0, 0
PURPLE = 136, 121, 181
SOFT_WHITE = 239, 239, 239
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255

LIGHT_COLOR = SOFT_WHITE
DARK_COLOR = PURPLE

SQ_SIZE = int(WIDTH / DIM) # 768/8 = 96
HIGHLIGHT_THICKNESS = 4

class Game:

    def __init__(self, title: str, size:tuple[int, int]):
        pygame.init()
        pygame.display.set_caption(title)
        self.screen = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()
        self.running = True
        self.highlighted = None

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
                    if len(self.clicks) > 1: # if the self.clicks licks is more than 2 long
                        self.state.move_piece(self.clicks)
                        self.clicks = []
                        self.highlighted = None
                    else: # check if the piece is of the correct color, if not clears the click log
                        if self.state.check_player_move(self.state.board[self.clicks[0][0]][self.clicks[0][1]]):
                            piece = self.state.board[self.clicks[0][0]][self.clicks[0][1]]
                            pos = self.clicks[0]
                            self.highlight_piece(pos)
                        else:
                            self.clicks = []
                
    def highlight_piece(self, pos:tuple):
        row, col = pos
        top_box = [col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE]
        self.highlighted = top_box

    def check_highlighted_piece(self):
        if self.highlighted != None:
            pygame.draw.rect(self.screen, RED, self.highlighted, HIGHLIGHT_THICKNESS)

    def load_images(self):
        self.images = {}
        for piece in self.pieces:
            self.images[piece] = pygame.transform.scale(pygame.image.load(f"Images/{piece}.png"), (SQ_SIZE, SQ_SIZE))

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
    game = Game("Chess!", size)
    game.new()

if __name__ == "__main__":
    main()
