import pygame
import pygame.freetype
import json  
import math
import os
import move as m
import engine as eg
import tkinter as tk
from tkinter import messagebox
import random

# Gets the config file
path = os.path.abspath(os.getcwd())
with open(os.path.join(path, "config.json")) as file:
    config = json.load(file)
    file.close()

# config preferences
LIGHT_COLOR = config["light_square_color"]
DARK_COLOR = config["dark_square_color"]
size = WIDTH, HEIGHT = config["resolution"]
MOVE_HLIGHT_COLOR = config["move_highlight_color"]
SELECT_COLOR = config["select_color"]
HIGHLIGHT_THICKNESS = config["highlight_thickness"]

# ALL CONSTANTS 
FPS = 30
DIM = 8 # 8x8 board
WHITE = 255, 255, 255
BLACK = 0, 0, 0
DARK_GRAY = 43, 45, 47
BASE_HLIGHT_LIST = ["  ", "  ", "  "]

BG_COLOR = DARK_GRAY
BEZEL = 70
BOARD_SCALER = 5

BOARD_SIZE = BOARD_WIDTH, BOARD_HEIGHT = HEIGHT-HEIGHT/(BOARD_SCALER), HEIGHT-HEIGHT/(BOARD_SCALER)
SQ_SIZE = int(BOARD_WIDTH / DIM)

X_OF_PROMOTION_TXT = 30
PROMOTION_BG_COLOR = WHITE
PROMOTION_TXT_COLOR = BLACK
PROMOTION_BOX_SIZE = SQ_SIZE - 20
PRO_TXT_OFFSET = 10
TXT_SIZE = 25

MOVE_LIST_COLOR = WHITE

# Game object: holds the methods and attributes
# for the display portion of the game of chess;
# relies on the engine for logic and gameplay
class Game:

    def __init__(self, title:str, size:tuple[int, int], type:str, player_team:str="w"):
        # Initializes the game window and the pygame module
        # Takes parameters title (title of the program),
        # size (resolution of the program), type
        # ("two_player" or "computer"), and the player's team.
        # if there are two players playing, this is empty.
        # Creates important objects and variables:
        # self.running (tells if the program is running), 
        # and self.clock (for keeping loops in check)
        pygame.init()

        pygame.display.set_caption(title)
        self.screen = pygame.display.set_mode(size)
        self.type = type
        self.player_team = player_team
        self.clock = pygame.time.Clock()
        self.running = True

    def new(self):
        # Creates all objects for actual interface and
        # logic, such as fonts, the current square selected
        # the squares that should be highlighted, the
        # game state, etc.

        # Creates the start position then starts the main
        # loop with self.run()
        self.font = pygame.freetype.SysFont(None, TXT_SIZE)
        self.move_list_font = pygame.freetype.SysFont(None, 20)
        self.square_selected = ()
        self.clicks = []
        self.highlighted = ["  ", "  ", "  "]
        self.buttons = None
        self.display_promotion = False
        self.state = eg.GameState()
        self.pieces = ['wP', 'bP', 'wK', 'bK', 'wQ', 'bQ', 'wB', 'bB', 'wN', 'bN', 'wR', 'bR']
        self.min_row, self.max_row = 1, 20

        self.load_images()
        self.state.create_start_pos()
        self.run()

    def run(self):
        # Main loop of the program, runs self.loop()
        # everytime the clock ticks
        while self.running:
            self.clock.tick(FPS)
            self.loop()
    
    def loop(self):
        # Draws everything to the screen, then
        # checks for events, then updates the screen
        self.draw()
        pygame.display.flip()
        self.events()
        self.check_computer_move()

    def check_computer_move(self):
        # If the game is played against a computer
        # and it is the computers move, play the
        # computer's move
        if self.type == "computer":
            if not self.state.white_to_move and self.player_team == "w":
                self.computer_move()
            elif self.state.white_to_move and self.player_team == "b":
                self.computer_move()

    def computer_move(self):
        # plays a "computer" move - currently
        # just plays a random move
        pygame.time.delay(1000)
        self.moves = self.state.all_legal_moves()
        move = random.choice(self.moves)
        self.successful_move(move)

    def events(self):
        # Checks for all events

        # Scrolling move list
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            if self.max_row < len(self.state.move_list)/2:
                self.min_row += 1
                self.max_row += 1
        if keys[pygame.K_UP]:
            if self.min_row > 1:
                self.min_row -= 1
                self.max_row -= 1

        for event in pygame.event.get():
            # Exits the program if the 'X' button is pressed
            if event.type == pygame.QUIT:
                exit()
            # Gets pos if a mouse button was clicked
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                
                # If the click was on the board
                if not (x > BOARD_WIDTH + BEZEL or y > BOARD_HEIGHT + BEZEL or x < BEZEL or y < BEZEL):
                    # column and row of square on chess board
                    col = ((x - BEZEL) // SQ_SIZE)
                    row = ((y - BEZEL) // SQ_SIZE)
                    self.click_on_the_board(row, col)
                    
    def click_on_the_board(self, row:int, col:int):
        # If same square is selected twice
        # reset everything
        if self.square_selected == (row, col):
            self.square_selected = ()
            self.clicks = []
            self.highlighted[0] = "  "
        # Otherwise, the current square selected
        # add the square_selected to the self.clicks
        # list
        else:
            self.square_selected = row, col
            self.clicks.append(self.square_selected)
            if self.type == "computer":
                if not self.player_team in self.state.board[self.clicks[0][0]][self.clicks[0][1]]:
                    return
            # if self.clicks contains two coordinates
            # on the board, play the move
            if len(self.clicks) == 2:
                self.play_move()
            # Otherwise, get the team of the piece
            # selected and highlight it if it is
            # from the team who's turn it is.
            # If it is not, reset self.clicks
            else:
                team = self.state.board[self.clicks[0][0]][self.clicks[0][1]][0]
                if (team == 'w' and self.state.white_to_move) or (team == 'b' and not self.state.white_to_move):
                    pos = self.clicks[0]
                    self.highlight_square(pos)
                    self.moves = self.state.all_legal_moves()
                else:
                    self.clicks = []

    def wait_for_promotion(self) -> str:
        # Display the buttons to promote a pawn
        # then wait until the user inputs a piece,
        # either through pressing a button,
        # or inputting a key
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
        # 1. gets the start_square and end_square of the
        #    move from the self.clicks list
        # 2. creates a Move object from it
        # 3. checks if the Move object is in the legal
        #    moves list
        # 4. if it is, highlight the move and call the
        #    the successful_move function, otherwise
        #    call the unsuccessful_move function
        start_square = self.clicks[0][0], self.clicks[0][1]
        end_square = self.clicks[1][0], self.clicks[1][1]
        move = m.Move(start_square, end_square, self.state.board, self.state.move_list)
        if move in self.moves: # if the move is legal
            self.successful_move(move)
        else: # otherwise, the move is illegal
            self.unsuccessful_move()

    def game_wins(self):
        # Tells who won the game, and asks
        # the user if another game should be played
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
        # Says that the game is a draw and asks
        # the user if the game should be be played again
        if messagebox.askyesno(title="Draw!", message="It's a Draw! Play Again?"):
            self.state.reset_game()
        else:
            exit()

    def successful_move(self, move:m.Move):
        # 1. Moves the piece on the board
        # 2. Checks special move types
        # 3. If the move list is long enough,
        #    the move list is automatically scrolled
        #    to the next line
        # 4. Resets self.clicks
        # 5. Flips the turn
        # 6. Checks if checkmate or stalemate are
        #    on the board
        # 7. Adds the algebraic notation of the move
        #    to the move list
        self.highlighted[0] = "  "
        self.highlight_move(move)
        self.state.move_piece(move)
        self.run_move_checks(move)

        if self.state.white_to_move and len(self.state.move_list)/2>20:
            self.min_row += 1
            self.max_row += 1

        self.clicks = []
        self.state.white_to_move = not self.state.white_to_move

        mate = self.state.check_mates()
        if mate == "checkmate":
            self.game_wins()
        elif mate == "stalemate":
            self.game_draws()

        if self.state.check:
            move.notation = move.notation + "+"

        self.state.move_list.append(move.notation)

    def unsuccessful_move(self):
        # if the second click is not an empty space and is on the correct team
        # then the highlighted piece changes
        # otherwise self.clicks resets and no piece is highlighted
        end_square = self.state.board[self.clicks[1][0]][self.clicks[1][1]]
        team = "w" if self.state.white_to_move else "b"
        if team in end_square:
            self.highlight_square(self.clicks[1])
            self.clicks = [self.clicks[1]]
        else:
            self.highlighted[0] = "  "
            self.clicks = []

    def run_move_checks(self, move:m.Move):
        # If the move is en passant, then get rid of the pawn
        # that is "en passant-ed"
        if move.enpassant:
            self.state.board[move.end_row + move.ep_direction][move.end_col] = "  "

        # If the move is promotion, wait for the user to
        # input a piece to promote to, then promote the
        # pawn to that piece and change the notation of
        # the move for promotion
        if move.promotion:
            promote_to = self.wait_for_promotion()
            self.promote(move.end_square, promote_to)
            self.display_promotion = False
            move.notation = move.notation + "=" + promote_to
            print(move.notation + "=" + promote_to)
        # if kingside castling, the rook that moves is -1 columns
        # away from the king, otherwise that rook is +1 columns away
        # the original rook position (a or h file) is either +1 or -2
        # columns away
        if move.castling:
            if move.end_square in [(7, 6), (0, 6)]:
                new_rook_col = -1
                old_rook_col = 1
            else:
                new_rook_col = 1
                old_rook_col = -2

            self.state.board[move.end_row][move.end_col+old_rook_col] = "  "
            self.state.board[move.end_row][move.end_col+new_rook_col] = move.piece_moved[0] + "R"

    def highlight_move(self, move:m.Move):
        # highlights the move passed as a parameter
        start_box = [move.start_col*SQ_SIZE+BEZEL, move.start_row*SQ_SIZE+BEZEL, SQ_SIZE, SQ_SIZE]
        end_box = [move.end_col*SQ_SIZE+BEZEL, move.end_row*SQ_SIZE+BEZEL, SQ_SIZE, SQ_SIZE]
        self.highlighted[1] = ((start_box, MOVE_HLIGHT_COLOR))
        self.highlighted[2] = ((end_box, MOVE_HLIGHT_COLOR))

    def highlight_square(self, square:tuple):
        # highlights the square passed as a parameter
        row, col = square
        box = [col*SQ_SIZE+BEZEL, row*SQ_SIZE+BEZEL, SQ_SIZE, SQ_SIZE]
        self.highlighted[0] = ((box, SELECT_COLOR))

    def draw_highlighted(self):
        # draws the highlighted squares if they are
        # in self.highlighted
        for i in self.highlighted:
            if i != "  ":
                pygame.draw.rect(self.screen, i[1], i[0], HIGHLIGHT_THICKNESS)

    def load_images(self):
        # loads the images necessary for the program
        # (i.e. pieces and icon images)
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
        # promotes the piece at position "pos" passed
        # as a parameter into the piece "to_promote"; also
        # passed as a parameter
        piece = self.state.board[pos[0]][pos[1]]
        self.state.board[pos[0]][pos[1]] = piece[0] + to_promote

    def draw(self):
        # draws all graphics to the window
        self.screen.fill(BG_COLOR)
        self.draw_board()
        self.draw_pieces()
        self.draw_move_list()
        self.draw_highlighted()
        if self.display_promotion == True:
            self.draw_promotion_buttons()

    def draw_move_list(self):
        # Draws the move list to the window
        i = 0
        for move in self.state.move_list:
            i += 1
            # if it is blacks move, the col is 60
            # pixels to the right, otherwise, it's 0
            col = 60 if i % 2 == 0 else 0
            # row is the index of the move divided by 2
            # always rounded up
            row = int(math.ceil(i/2))
            # display_row is where the row is visually
            # placed, it is always placed at the
            # row - (self.max_row - 20)
            display_row = row - (self.max_row - 20)
            # if it is white's move add the move number
            # to the front of the string to display
            if i % 2 == 1:
                move = str(row) + "." + move
            # if the row is <= the max row to display
            # and is >= the min row to display, render it
            if row <= self.max_row and row >= self.min_row:
                self.move_list_font.render_to(self.screen, (BOARD_WIDTH+(col*2)+BEZEL+60, display_row*30+BEZEL), move, MOVE_LIST_COLOR)

    def draw_promotion_buttons(self):
        # draws the promotion buttons
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
        # Draws board
        colors = [LIGHT_COLOR, DARK_COLOR]

        for r in range(DIM):
            for c in range(DIM):
                # if the sum of r and c is even, the square
                # is a light color, otherwise it is odd
                # (ex: (0,0) is a light square, but (0,1)
                # is a dark square)
                color = colors[(r + c) % 2]
                pygame.draw.rect(self.screen, color, pygame.Rect(c*SQ_SIZE+BEZEL, r*SQ_SIZE+BEZEL, SQ_SIZE, SQ_SIZE))

    def draw_pieces(self):
        # draws the pieces
        for r in range(DIM):
            for c in range(DIM):
                piece = self.state.board[r][c]
                if piece != "  ":
                    self.screen.blit(self.images[piece], (SQ_SIZE*c+BEZEL, SQ_SIZE*r+BEZEL))

def main():
    # creates game
    game = Game("Chess", size, "computer")
    game.new()

if __name__ == "__main__":
    # runs main if this exact file is run
    main()
