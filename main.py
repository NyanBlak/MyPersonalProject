import chess
import os
import json
import pygame
from pygame.freetype import STYLE_NORMAL, STYLE_OBLIQUE, STYLE_STRONG, STYLE_UNDERLINE, STYLE_WIDE

path = os.path.abspath(os.getcwd())
with open(os.path.join(path, "config.json")) as file:
    config = json.load(file)
    file.close()

light_square = config["light_square_color"]
dark_square = config["dark_square_color"]

dark_mode = True if os.system("defaults read -g AppleInterfaceStyle") == 0 else False

CHESS_WIDTH = CHESS_HEIGHT = config["resolution"]

WIDTH = HEIGHT = 400
size = WIDTH, HEIGHT

title = "Main Menu"
FPS = 15

WHITE = 255, 255, 255
GRAY = 125, 125, 125
DARK_GRAY = 43, 45, 47
BLACK = 0, 0, 0

X_OFFSET = 40
if dark_mode:
	BG_COLOR = DARK_GRAY
	TITLE_TXT_COLOR = light_square
	TXT_COLOR = DARK_GRAY
	BTN_COLOR = light_square
else:
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
		self.title_font = pygame.freetype.SysFont(None, 60, bold=True)
		self.title_font.style = eval(config["title_style"])
		self.font = pygame.freetype.SysFont(None, 20)

		self.button_dict = {}
		self.text_dict = {}
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
			if event.type == pygame.MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
				buttons = list(self.button_dict.values())
				keys = list(self.button_dict.keys())
				for button in buttons:
					if pos[0] > button.left and pos[0] < button.left + button.width:
						if pos[1] > button.top and pos[1] < button.top + button.height:
							i = buttons.index(button)
							func, text = keys[i]
							if (text == "White" or text == "Black") and not self.getting_color:
								continue
							func()
    
	def draw(self):
		self.screen.fill(BG_COLOR)
		self.draw_buttons()
		self.draw_text()
		pygame.display.flip()

	def draw_buttons(self):
		w, h = 150, 50
		two_player_button = pygame.Rect(X_OFFSET, 120, w, h)
		self.white_button = pygame.Rect(X_OFFSET, 180, w/2-10, h)
		self.black_button = pygame.Rect(X_OFFSET+(w/2+10), 180, w/2-10, h)
		computer_button = pygame.Rect(X_OFFSET, 180, w, h)
		exit_button = pygame.Rect(X_OFFSET, 240, w, h)
		
		self.button_dict[self.play_two_player, "2 Player"] = two_player_button
		self.button_dict[self.get_color, "Computer"] = computer_button
		self.button_dict[exit, "Exit"] = exit_button

		for button in self.button_dict.values():
			if button == computer_button and self.getting_color:
				pygame.draw.rect(self.screen, BTN_COLOR, self.white_button)
				pygame.draw.rect(self.screen, BTN_COLOR, self.black_button)
				continue
			elif button == self.white_button or button == self.black_button:
				continue
			pygame.draw.rect(self.screen, BTN_COLOR, button)

	def draw_text(self):
		# font.render_to(screen, (x, y), text, color)
		title = "Chess!"
		self.title_font.render_to(self.screen,(X_OFFSET-10, 40), title, (TITLE_TXT_COLOR))

		buttons = list(self.button_dict.values())
		keys = list(self.button_dict.keys())
		for button in buttons:
			i = buttons.index(button)
			text = keys[i][1]
			if text == "Computer" and self.getting_color:
				self.font.render_to(self.screen, (X_OFFSET+2, button.top + button.height/2 - 2), "White", (TXT_COLOR))
				self.font.render_to(self.screen, (X_OFFSET+2+(button.width/2+10), button.top + button.height/2 - 2), "Black", (TXT_COLOR))
				continue
			elif text == "White" or text == "Black":
				continue
			self.font.render_to(self.screen, (X_OFFSET+2, button.top + button.height/2 - 2), text, (TXT_COLOR))

	def get_color(self):
		self.getting_color = True
		self.button_dict[lambda: self.play_computer("w"), "White"] = self.white_button
		self.button_dict[lambda: self.play_computer("b"), "Black"] = self.black_button

	def play_computer(self, color:str):
		width, height = config["resolution"]
		game = chess.Game("Chess", (width, height), "computer", color)
		game.new()

	def play_two_player(self):
		width, height = config["resolution"]
		game = chess.Game("Chess", (width, height), "two_player")
		game.new()

if __name__ == "__main__":
    menu = MainMenu(title, size)
    menu.new()
