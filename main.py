import chess
import os
import json
import pygame
import sprites
import webbrowser
from pygame.freetype import STYLE_NORMAL, STYLE_OBLIQUE, STYLE_STRONG, STYLE_UNDERLINE, STYLE_WIDE

# The config.json file can be edited for whatever the
# user wishes the changes to be. The config includes:
#   1. Resolution
#   2. Light Square Color
#   3. Dark Square Color
#   4. Pieces set
#   5. Select color
#   6. Move highlight color
#   7. Highlight thickness

# Path to the current directory, used for reading the
# 'config.json' file as well as for loading the images
path = "".join(os.path.split(__file__)[:-1])
with open(os.path.join(path, "config.json")) as file:
    config = json.load(file)
    file.close()

# Gets light and dark square colors from the
# config
light_square = config["light_square_color"]
dark_square = config["dark_square_color"]

# board has to be a square so the width and the
# height equal to the resolution
CHESS_WIDTH = CHESS_HEIGHT = config["resolution"]

# Size of main menu
WIDTH, HEIGHT = 400, 600
size = WIDTH, HEIGHT

# Title and FPS of window
title = "Main Menu"
FPS = 15

# Constant Colors
WHITE = 255, 255, 255
GRAY = 125, 125, 125
DARK_GRAY = 43, 45, 47
BLACK = 0, 0, 0

# Easily changable constant colors
BG_COLOR = WHITE
TITLE_TXT_COLOR = BLACK
TXT_COLOR = WHITE
BTN_COLOR = BLACK

# Main Menu Class
class MainMenu:

	def __init__(self, title, size):
		# Initializes main menu
		pygame.init()
		pygame.display.set_caption(title)
		self.screen = pygame.display.set_mode(size)
		self.clock = pygame.time.Clock()

	def new(self):
		# Creates all required objects and
		# variables for the main menu, including:
		# fonts, sprites, etc.
		W, H = 64*3, 32*3
		TITLE_W, TITLE_H = 64*5, 32*5
		Y, Y_INC = 200, 100
		CENTER = WIDTH/2 - W/2
		TITLE_CENTER = WIDTH/2 - TITLE_W/2
		self.all_sprites = pygame.sprite.Group()
		self.buttons = pygame.sprite.Group()
		self.title_font = pygame.font.SysFont("Menlo", 70, bold=True) 
		self.font = pygame.font.SysFont("Menlo", 24, bold=True)
		self.smaller_font = pygame.font.SysFont("Menlo", 18, bold=True)
		self.getting_color = False

		buttons = [
			sprites.Button(TITLE_CENTER, 30, TITLE_W, TITLE_H, self.show_credits, "Chess", TXT_COLOR, self.title_font),
			sprites.Button(CENTER, Y, W, H, self.play_two_player, "2 Player", TXT_COLOR, self.font),
			sprites.Button(CENTER, Y+Y_INC, (W/2-10), H, lambda:self.play_computer(True), "White", TXT_COLOR, self.smaller_font, val=1),
			sprites.Button(CENTER+(W/2+10), Y+Y_INC, (W/2-10), H, lambda:self.play_computer(False), "Black", TXT_COLOR, self.smaller_font, val=1),
			sprites.Button(CENTER, Y+Y_INC, W, H, self.get_color, "Computer", TXT_COLOR, self.font, val=0),
			sprites.Button(CENTER, Y+(2*Y_INC), W, H, exit, "Quit", TXT_COLOR, self.font)
		]
		self.buttons.add(buttons)
		self.all_sprites.add(buttons)

		self.run()

	def run(self):
		# Main loop of the program, the clock
		# ticks for FPS times a second and then
		# loop is called after the clock ticks
		while True:
			self.clock.tick(FPS)
			self.loop()
    
	def loop(self):
		# Draws everything to the screen,
		# Checks for events, then updates
		# the screen
		self.draw()
		self.events()
		pygame.display.flip()

	def events(self):
		# Checks for events, also sends
		# the events to each button's
		# handle_event() function
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()
			for button in self.buttons:
				if button.val == 0 and self.getting_color:
					continue
				elif button.val == 1 and not self.getting_color:
					continue
				button.handle_event(event)
    
	def draw(self):
		# Fills the screen, then draws sprites
		self.screen.fill(BG_COLOR)
		self.draw_sprites()

	def draw_sprites(self):
		# Draws sprites, also checks if the user
		# is getting_color
		for sprite in self.all_sprites:
			if sprite.val == 0 and self.getting_color:
				continue
			elif sprite.val == 1 and not self.getting_color:
				continue
			sprite.draw(self.screen)

	def get_color(self):
		# Function to start getting color
		self.getting_color = True

	def play_computer(self, player_is_white:bool):
		# Starts playing chess against the computer.
		# Takes bool parameter "player_is_white" to
		# figure out which color the player plays as 
		color = "w" if player_is_white else "b"
		width, height = config["resolution"]
		game = chess.Game("Chess", (width, height), "computer", color)
		game.new()

	def play_two_player(self):
		# Starts playing chess against another player
		width, height = config["resolution"]
		game = chess.Game("Chess", (width, height), "two_player")
		game.new()

	def show_credits(self):
		# Opens github repository for this project
		webbrowser.open("https://github.com/NyanBlak/MyPersonalProject")

def main():
	# creates MainMenu object and makes
	# a new main menu
	menu = MainMenu(title, size)
	menu.new()

if __name__ == "__main__":
	# checks if file was imported,
	# if it wasnt, run main()
	main()
