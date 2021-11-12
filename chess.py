import pygame
import pygame.freetype
import json  
import math
import os
import sprites
from pymsgbox import  * 
import computer as c
import move as m
import engine as eg
import random

# Gets the config file
path = "".join(os.path.split(__file__)[:-1])
with open(os.path.join(path, "config.json")) as file:
    config = json.load(file)
    file.close()

# config preferences
LIGHT_COLOR = config["light_square_color"]
DARK_COLOR = config["dark_square_color"]
size = WIDTH, HEIGHT = config["resolution"]
LIGHT_HIGHLIGHT_COLOR = config["light_highlight_color"]
DARK_HIGHLIGHT_COLOR = config["dark_highlight_color"]

# ALL CONSTANTS 
FPS = 30
DIM = 8 # 8x8 board
WHITE = 255, 255, 255
BLACK = 0, 0, 0
DARK_GRAY = 43, 45, 47

BG_COLOR = DARK_GRAY
BEZEL = 70
BOARD_SCALER = 5

BOARD_WIDTH, BOARD_HEIGHT = HEIGHT-HEIGHT/(BOARD_SCALER), HEIGHT-HEIGHT/(BOARD_SCALER)
BOARD_SIZE = BOARD_WIDTH, BOARD_HEIGHT
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
        self.highlighted_square = ()
        self.highlighted_move = ()
        self.buttons = None
        self.display_promotion = False
        self.state = eg.GameState()
        self.pieces = ['wP', 'bP', 'wK', 'bK', 'wQ', 'bQ', 'wB', 'bB', 'wN', 'bN', 'wR', 'bR']
        self.min_row, self.max_row = 1, 20

        self.create_sprites()
        self.load_images()
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
        self.check_computer_move()
        self.events()

    def wait(self, sprites:pygame.sprite.Group):
        while True:
            for event in pygame.event.get():
                if event == pygame.QUIT:
                    exit()
                for sprite in sprites:
                    sprite.handle_event(event)
                    if sprite.button_down:
                        return sprite
            self.draw()
            pygame.display.flip()

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
            for sprite in self.all_sprites:
                sprite.handle_event(event)
    
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
        comp_num = 1 if self.state.white_to_move else -1
        cpu = c.Computer(self.state, comp_num)
        move = cpu.get_move()
        self.successful_move(move)

    def click_on_the_board(self, row:int, col:int):
        # If same square is selected twice
        # reset everything
        if self.square_selected == (row, col):
            self.square_selected = ()
            self.clicks = []
            self.highlighted_square = ()
        # Now, is the square pressed an empty square
        # and self.clicks has no clicks in it, end the
        # function
        elif len(self.clicks) == 0 and self.state.board[row][col] == "  ":
            return
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
            return

    def game_wins(self):
        # Tells who won the game, and asks
        # the user if another game should be played
        if self.state.white_to_move:
            winner = "Black Wins! "
        else:
            winner = "White Wins! "
        if prompt(text=winner, title=winner):
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
        self.highlighted_square = ()
        self.highlight_move(move)
        self.state.move_piece(move)
        self.run_move_checks(move)

        if self.state.white_to_move and len(self.state.move_list)/2>20:
            self.min_row += 1
            self.max_row += 1

        self.clicks = []
        self.square_selected = None
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
            self.highlighted_square = ()
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
            self.display_promotion = True
            sprite = self.wait(self.promotion_buttons)
            to_promote = sprite.text
            self.state.board[move.end_row][move.end_col] = self.state.get_team() + to_promote
            self.display_promotion = False
            move.notation = move.notation + "="
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
        self.highlighted_move = ((move.start_row, move.start_col), (move.end_row, move.end_col))

    def highlight_square(self, square:tuple):
        # highlights the square passed as a parameter
        row, col = square
        self.highlighted_square = (row, col)

    def create_sprites(self):
        self.all_sprites = pygame.sprite.Group()
        self.promotion_buttons = pygame.sprite.Group()
        self.buttons = pygame.sprite.Group()
        
        to_display = ["Q", "N", "R", "B"]
        STARTING_X, INC_X = 10, 5
        for i in range(4):
             self.promotion_buttons.add(sprites.Button(STARTING_X + BEZEL + (PROMOTION_BOX_SIZE * (i)) + (INC_X * i), BOARD_HEIGHT+PRO_TXT_OFFSET+BEZEL, PROMOTION_BOX_SIZE, PROMOTION_BOX_SIZE, lambda:self.promote(to_display[i]), to_display[i]))

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

    def draw(self):
        # draws all graphics to the window
        self.screen.fill(BG_COLOR)
        self.draw_sprites()
        self.draw_board()
        self.draw_pieces()
        self.draw_move_list()

    def draw_sprites(self):
        if self.display_promotion == True:
            self.promotion_buttons.draw(self.screen)
        self.all_sprites.draw(self.screen)

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

    def draw_board(self):
        # Draws board
        colors = [LIGHT_COLOR, DARK_COLOR]
        highlight_colors = [LIGHT_HIGHLIGHT_COLOR, DARK_HIGHLIGHT_COLOR]
        for r in range(DIM):
            for c in range(DIM):
                # if the sum of r and c is even, the square
                # is a light color, otherwise it is odd
                # (ex: (0,0) is a light square, but (0,1)
                # is a dark square)
                index = (r + c) % 2
                if ((r, c) == self.highlighted_square) or ((r, c) in self.highlighted_move):
                    pygame.draw.rect(self.screen, highlight_colors[index], pygame.Rect(c*SQ_SIZE+BEZEL, r*SQ_SIZE+BEZEL, SQ_SIZE, SQ_SIZE))
                    continue
                pygame.draw.rect(self.screen, colors[index], pygame.Rect(c*SQ_SIZE+BEZEL, r*SQ_SIZE+BEZEL, SQ_SIZE, SQ_SIZE))

    def draw_pieces(self):
        # draws the pieces
        for r in range(DIM):
            for c in range(DIM):
                piece = self.state.board[r][c]
                if piece != "  ":
                    self.screen.blit(self.images[piece], (SQ_SIZE*c+BEZEL, SQ_SIZE*r+BEZEL))

def main():
    # creates game
    game = Game("Chess", size, "two_player")
    game.new()

if __name__ == "__main__":
    # runs main if this exact file is run
    main()
