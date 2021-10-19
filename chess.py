from tkinter.constants import Y
import pygame
import pygame.freetype
import json  
import math
import os
import move as m
import engine as eg
import tkinter as tk
from tkinter import messagebox

path = os.path.abspath(os.getcwd())

with open(os.path.join(path, "config.json")) as file:
    config = json.load(file)
    file.close()

FPS = 30
DIM = 8 # 8x8 board
WHITE = 255, 255, 255
BLACK = 0, 0, 0
BASE_HLIGHT_LIST = ["  ", "  ", "  "]

BG_COLOR = BLACK
BEZEL = 70
BOARD_SCALER = 5

LIGHT_COLOR = config["light_square_color"]
DARK_COLOR = config["dark_square_color"]
size = WIDTH, HEIGHT = config["resolution"]
MOVE_HLIGHT_COLOR = config["move_highlight_color"]
SELECT_COLOR = config["select_color"]
HIGHLIGHT_THICKNESS = config["highlight_thickness"]

BOARD_SIZE = BOARD_WIDTH, BOARD_HEIGHT = HEIGHT-HEIGHT/(BOARD_SCALER), HEIGHT-HEIGHT/(BOARD_SCALER)
SQ_SIZE = int(BOARD_WIDTH / DIM)

X_OF_PROMOTION_TXT = 30
PROMOTION_BG_COLOR = WHITE
PROMOTION_TXT_COLOR = BLACK
PROMOTION_BOX_SIZE = SQ_SIZE - 20
PRO_TXT_OFFSET = 10
TXT_SIZE = 25

MOVE_LIST_COLOR = WHITE

class Game:

    def __init__(self, title: str, size:tuple[int, int], type:str):
        pygame.init()

        pygame.display.set_caption(title)
        self.screen = pygame.display.set_mode(size)
        self.type = type
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = pygame.freetype.SysFont(None, TXT_SIZE)
        self.move_list_font = pygame.freetype.SysFont(None, 20)

        self.highlighted = ["  ", "  ", "  "]
        self.buttons = None
        self.display_promotion = False
        self.state = eg.GameState()
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
            self.loop()
    
    def loop(self):
        self.draw()
        self.events()
        pygame.display.flip()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = x, y = pygame.mouse.get_pos()
                if x > BOARD_WIDTH + BEZEL or y > BOARD_HEIGHT + BEZEL or x < BEZEL or y < BEZEL:
                    return
                col = ((x - BEZEL) // SQ_SIZE)
                row = ((y - BEZEL) // SQ_SIZE)

                if self.square_selected == (row, col): # If same square is selected twice
                    self.square_selected = ()
                    self.clicks = []
                    self.highlighted[0] = "  "
                else:
                    self.square_selected = row, col
                    self.clicks.append(self.square_selected)
                    if len(self.clicks) == 2: # if the self.clicks licks is 2 long
                        self.play_move()
                    else: # First click, check if the piece is of the correct color, if not clears the click log
                        piece = self.state.board[self.clicks[0][0]][self.clicks[0][1]]
                        team = piece[0]
                        if (team == 'w' and self.state.white_to_move) or (team == 'b' and not self.state.white_to_move):
                            pos = self.clicks[0]
                            self.highlight_piece(pos)
                            self.moves = self.state.all_legal_moves()
                        else:
                            self.clicks = []

    def wait_for_promotion(self) -> str:
        while True:
            self.display_promotion = True
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n or event.key == pygame.K_k:
                        return "N"
                    elif event.key == pygame.K_r:
                        return "R"
                    elif event.key == pygame.K_q:
                        return "Q"
                    elif event.key == pygame.K_b:
                        return "B"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    x, y = pos
                    # self.promotion_rects [queen, rook, knight, bishop]
                    if x > self.promotion_rects[0].left and x < self.promotion_rects[0].right:
                        if y > self.promotion_rects[0].top and y < self.promotion_rects[0].bottom:
                            return "Q"
                    if x > self.promotion_rects[1].left and x < self.promotion_rects[1].right:
                        if y > self.promotion_rects[1].top and y < self.promotion_rects[1].bottom:
                            return "R"
                    if x > self.promotion_rects[2].left and x < self.promotion_rects[2].right:
                        if y > self.promotion_rects[2].top and y < self.promotion_rects[2].bottom:
                            return "N"
                    if x > self.promotion_rects[3].left and x < self.promotion_rects[3].right:
                        if y > self.promotion_rects[3].top and y < self.promotion_rects[3].bottom:
                            return "B"
            self.draw()
            pygame.display.flip()
            

    def play_move(self):
        start_square = self.clicks[0][0], self.clicks[0][1]
        end_square = self.clicks[1][0], self.clicks[1][1]
        move = m.Move(start_square, end_square, self.state.board, self.state.move_list)
        if move in self.moves: # if the move is legal
            self.highlight_move(move)
            self.successful_move(move)
            print(self.state.move_list)
        else: # otherwise, the move is illegal
            self.unsuccesful_move()

    def game_wins(self):
        if self.state.white_to_move:
            pygame.display.set_icon(self.icon_b)
            winner = "Black Wins! "
        else:
            pygame.display.set_icon(self.icon_w)
            winner = "White Wins! "
        if messagebox.askyesno(title=winner,message=winner + "Play Again?"):
            self.state.reset_game()
        else:
            exit()

    def game_draws(self):
        if messagebox.askyesno(title="Draw!", message="It's a Draw! Play Again?"):
            self.state.reset_game()
        else:
            exit()

    def successful_move(self, move:m.Move):
        self.state.move_piece(move, self.state.board)
        self.run_move_checks(move)

        self.clicks = []
        self.state.white_to_move = not self.state.white_to_move

        mate = self.state.check_mates()
        if mate == "checkmate":
            self.game_wins()
        elif mate == "stalemate":
            self.game_draws()

        self.state.move_list.append(move.notation)

    def unsuccesful_move(self):
        # if the second click is not an empty space and is on the correct team
        # then the highlighted piece changes
        # otherwise self.clicks resets and no piece is highlighted
        end_square = self.state.board[self.clicks[1][0]][self.clicks[1][1]]
        team = "w" if self.state.white_to_move else "b"
        if team in end_square:
            self.highlight_piece(self.clicks[1])
            self.clicks = [self.clicks[1]]
        else:
            self.highlighted[0] = "  "
            self.clicks = []

    def run_move_checks(self, move):
        if move.enpassant:
            self.state.board[move.end_row + move.ep_direction][move.end_col] = "  "

        if move.promotion:
            promote_to = self.wait_for_promotion()
            self.promote(move.end_square, promote_to)
            self.display_promotion = False
            move.notation = move.notation + "=" + promote_to

        if move.castling:
            # if kingside castling, the rook that moves is -1 columns
            # away from the king, otherwise that rook is +1 columns away
            # the original rook position (a or h file) is either +1 or -2
            # columns away
            if move.end_square in [(7, 6), (0, 6)]:
                new_rook_col = -1
                old_rook_col = 1
            else:
                new_rook_col = 1
                old_rook_col = -2

            self.state.board[move.end_row][move.end_col+old_rook_col] = "  "
            self.state.board[move.end_row][move.end_col+new_rook_col] = move.piece_moved[0] + "R"

    def reset_highlighted(self):
        self.highlighted = ["  ", "  ", "  "]

    def highlight_move(self, move):
        start_box = [move.start_col*SQ_SIZE+BEZEL, move.start_row*SQ_SIZE+BEZEL, SQ_SIZE, SQ_SIZE]
        end_box = [move.end_col*SQ_SIZE+BEZEL, move.end_row*SQ_SIZE+BEZEL, SQ_SIZE, SQ_SIZE]
        self.highlighted[1] = ((start_box, MOVE_HLIGHT_COLOR))
        self.highlighted[2] = ((end_box, MOVE_HLIGHT_COLOR))

    def highlight_piece(self, pos:tuple):
        row, col = pos
        box = [col*SQ_SIZE+BEZEL, row*SQ_SIZE+BEZEL, SQ_SIZE, SQ_SIZE]
        self.highlighted[0] = ((box, SELECT_COLOR))

    def check_highlighted(self):
        for i in self.highlighted:
            if i != "  ":
                pygame.draw.rect(self.screen, i[1], i[0], HIGHLIGHT_THICKNESS)

    def load_images(self):
        self.icon_w = pygame.image.load(os.path.join(path, "Images", "Icon0.png"))
        self.icon_b = pygame.image.load(os.path.join(path, "Images", "Icon1.png"))
        pygame.display.set_icon(self.icon_w)
        self.images = {}
        for piece in self.pieces:
            self.images[piece] = pygame.transform.scale(
                pygame.image.load(
                    os.path.join(path, "Themes", f"{config['theme_set']}", f"{piece}.png")),
                    (SQ_SIZE, SQ_SIZE)
            )

    def promote(self, pos:tuple[int, int], to_promote):
        piece = self.state.board[pos[0]][pos[1]]
        self.state.board[pos[0]][pos[1]] = piece[0] + to_promote

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.draw_board()
        self.draw_pieces()
        self.draw_move_list()
        self.check_highlighted()
        if self.display_promotion == True:
            self.draw_promotion_text()

    def draw_move_list(self):
        i = 0
        for move in self.state.move_list:
            i += 1
            col = 60 if i % 2 == 0 else 0
            row = int(math.ceil(i/2))
            if i % 2 == 1:
                move = str(row) + "." + move
            if row > 20:
                inc = 1
                if row > 40:
                    inc = 2
                col += 120 * inc
                row -= 20 * inc
            self.move_list_font.render_to(self.screen, (BOARD_WIDTH+(col*2)+BEZEL+60, row*30+BEZEL), move, MOVE_LIST_COLOR)

    def draw_promotion_text(self):
        self.promotion_rects = []
        to_display = ["Q", "N", "R", "B"]
        STARTING_X = 10
        INC_X = 5
        for i in range(4):
            rect = pygame.Rect(STARTING_X + BEZEL + (PROMOTION_BOX_SIZE * (i)) + (INC_X * i), BOARD_HEIGHT+PRO_TXT_OFFSET+BEZEL, PROMOTION_BOX_SIZE, PROMOTION_BOX_SIZE)
            self.promotion_rects.append(rect)
        for object in self.promotion_rects:
            i = self.promotion_rects.index(object)
            pygame.draw.rect(self.screen, PROMOTION_BG_COLOR, object)
            self.font.render_to(self.screen, (object.centerx, object.centery), to_display[i], PROMOTION_TXT_COLOR)

    def draw_board(self):
        colors = [LIGHT_COLOR, DARK_COLOR]

        for r in range(DIM):
            for c in range(DIM):
                color = colors[(r + c) % 2]
                pygame.draw.rect(self.screen, color, pygame.Rect(c*SQ_SIZE+BEZEL, r*SQ_SIZE+BEZEL, SQ_SIZE, SQ_SIZE))

    def draw_pieces(self):
        for r in range(DIM):
            for c in range(DIM):
                piece = self.state.board[r][c]
                if piece != "  ":
                    self.screen.blit(self.images[piece], (SQ_SIZE*c+BEZEL, SQ_SIZE*r+BEZEL))

def main():
    game = Game("Chess", size, "two_player")
    game.new()

if __name__ == "__main__":
    main()
