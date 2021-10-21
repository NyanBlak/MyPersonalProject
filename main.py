import chess
import os
import json
import pygame
import sprites
from pygame.freetype import STYLE_NORMAL, STYLE_OBLIQUE, STYLE_STRONG, STYLE_UNDERLINE, STYLE_WIDE

path = os.path.abspath(os.getcwd())
with open(os.path.join(path, "config.json")) as file:
    config = json.load(file)
    file.close()

light_square = config["light_square_color"]
dark_square = config["dark_square_color"]

CHESS_WIDTH = CHESS_HEIGHT = config["resolution"]

WIDTH = HEIGHT = 400
size = WIDTH, HEIGHT

title = "Main Menu"
FPS = 15

WHITE = 255, 255, 255
GRAY = 125, 125, 125
DARK_GRAY = 43, 45, 47
BLACK = 0, 0, 0

BG_COLOR = WHITE
TITLE_TXT_COLOR = BLACK
TXT_COLOR = WHITE
BTN_COLOR = BLACK

class MainMenu:

	def __init__(self, title, size):
		pygame.init()
		pygame.display.set_caption(title)
		self.screen = pygame.display.set_mode(size)
		self.clock = pygame.time.Clock()

	def new(self):
		W, H = 64*2, 32*2
		TITLE_W, TITLE_H = 64*4, 32*4
		Y, Y_INC = 170, 70
		CENTER = WIDTH/2 - W/2
		TITLE_CENTER = WIDTH/2 - TITLE_W/2
		self.all_sprites = pygame.sprite.Group()
		self.buttons = pygame.sprite.Group()
		self.title_font = pygame.font.SysFont(None, 80)
		self.title_font.set_bold(True)
		self.title_font.set_underline(True)
		self.font = pygame.font.SysFont(None, 24)

		buttons = [
			sprites.Button(TITLE_CENTER, 30, TITLE_W, TITLE_H, self.show_credits, "Chess", TXT_COLOR, self.title_font),
			sprites.Button(CENTER, Y, W, H, self.play_two_player, "2 Player", TXT_COLOR, self.font),
			sprites.Button(CENTER, Y+Y_INC, (W/2-10), H, lambda:self.play_computer(True), "White", TXT_COLOR, self.font),
			sprites.Button(CENTER+(W/2+10), Y+Y_INC, (W/2-10), H, lambda:self.play_computer(False), "Black", TXT_COLOR, self.font),
			sprites.Button(CENTER, Y+Y_INC, W, H, self.get_color, "Computer", TXT_COLOR, self.font),
			sprites.Button(CENTER, Y+(2*Y_INC), W, H, exit, "Quit", TXT_COLOR, self.font)
		]
		self.buttons.add(buttons)
		self.all_sprites.add(buttons)

		self.getting_color = False
		self.run()

	def run(self):
		while True:
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
			for button in self.buttons:
				if (button.text == "Computer") and self.getting_color:
					continue
				elif (button.text == "White" or button.text == "Black") and not self.getting_color:
					continue
				button.handle_event(event)
    
	def draw(self):
		self.screen.fill(BG_COLOR)
		self.draw_sprites()
		pygame.display.flip()

	def draw_sprites(self):
		for sprite in self.all_sprites:
			if (sprite.text == "Computer") and self.getting_color:
				continue
			elif (sprite.text == "White" or sprite.text == "Black") and not self.getting_color:
				continue
			sprite.draw(self.screen)

	def get_color(self):
		self.getting_color = True

	def play_computer(self, player_is_white:bool):
		color = "w" if player_is_white else "b"
		width, height = config["resolution"]
		game = chess.Game("Chess", (width, height), "computer", color)
		game.new()

	def play_two_player(self):
		width, height = config["resolution"]
		game = chess.Game("Chess", (width, height), "two_player")
		game.new()

	def show_credits(self):
		print("insert credits here")
        # Draws the move list to the window
if __name__ == "__main__":
    menu = MainMenu(title, size)
    menu.new()
