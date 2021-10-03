import pygame
import json
from engine import *

FPS = 15
DIM = 8 # 8x8 board
WHITE = 255, 255, 255

with open("config.json") as file:
    config = json.load(file)
    file.close()

LIGHT_COLOR = config["light_square_color"]
DARK_COLOR = config["dark_square_color"]
WIDTH = HEIGHT = config["resolution"]
HIGHLIGHT_COLOR = config["highlight_color"]
HIGHLIGHT_THICKNESS = config["highlight_thickness"]

size = WIDTH, HEIGHT 
SQ_SIZE = int(WIDTH / DIM) # 768/8 = 96

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
                        self.play_move()
                    else: # First click, check if the piece is of the correct color, if not clears the click log
                        piece = self.state.board[self.clicks[0][0]][self.clicks[0][1]]
                        if self.state.check_player_move(piece):
                            pos = self.clicks[0]
                            self.highlight_piece(pos)
                        else:
                            self.clicks = []

    def play_move(self):
        start_square = self.clicks[0][0], self.clicks[0][1]
        end_square = self.clicks[1][0], self.clicks[1][1]
        move = Move(start_square, end_square, self.state.board)
        if move.is_move_legal(self.moves): # if the move is legal
            self.successful_move(move)
        else: # otherwise, the move is illegal
            self.unsuccesful_move()

    def successful_move(self, move):
        self.state.move_list.append(move.notation)
        move.check_enpassant(self.state.white_to_move, self.state.move_list, self.state.board)
        move.move_piece()
        promotion = self.state.check_promotion(move.end_square)
        
        if promotion:
            self.promote(move.end_square)

        if move.castling:
            # if kingside castling, rook is -1 away from the king, otherwise its 1 away
            if move.end_square in [(7, 6), (0, 6)]:
                new_rook_col = -1
                old_rook_col = 1
            else:
                new_rook_col = 1
                old_rook_col = -2

            self.state.board[move.end_row][move.end_col+old_rook_col] = " "
            self.state.board[move.end_row][move.end_col+new_rook_col] = move.piece_moved[0] + "R"

        self.clicks = []
        self.highlighted = None
        self.state.white_to_move = not self.state.white_to_move
        print(self.state.move_list[-1])

    def unsuccesful_move(self):
        if self.state.board[self.clicks[1][0]][self.clicks[1][1]] != " ":
            self.highlight_piece(self.clicks[1])
            self.clicks = [self.clicks[1]]
        else:
            self.highlighted = None
            self.clicks = []


    def highlight_piece(self, pos:tuple):
        row, col = pos
        box = [col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE]
        self.moves = self.state.all_legal_moves()
        self.highlighted = box

    def check_highlighted_piece(self):
        if self.highlighted != None:
            pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, self.highlighted, HIGHLIGHT_THICKNESS)

    def load_images(self):
        self.images = {}
        for piece in self.pieces:
            self.images[piece] = pygame.transform.scale(pygame.image.load(f"Themes/{config['theme_set']}/{piece}.png"), (SQ_SIZE, SQ_SIZE))

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
