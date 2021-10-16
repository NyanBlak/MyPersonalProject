import chessmain as chess
import os
import json
import pygame

path = os.path.abspath(os.getcwd())
with open(os.path.join(path, "config.json")) as file:
    config = json.load(file)
    file.close()

CHESS_WIDTH = CHESS_HEIGHT = config["resolution"]

WIDTH = HEIGHT = 400
size = WIDTH, HEIGHT

title = "Main Menu"
FPS = 15

WHITE = 255, 255, 255
BLACK = 0, 0, 0

class Game:

	def __init__(self, title, size):
		pygame.init()
		pygame.display.set_caption(title)
		self.screen = pygame.display.set_mode(size)
		self.clock = pygame.time.Clock()
		self.button_dict = {}

	def new(self):
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
    
	def draw(self):
		self.screen.fill(WHITE)
		self.draw_buttons()
		pygame.display.flip()
	
	def draw_buttons(self):
		two_player_button = pygame.Rect(WIDTH/2-20, HEIGHT/2, 40, 20)
		
		self.button_dict[two_player_button] = self.run_two_player
		pygame.draw.rect(self.screen, BLACK, two_player_button)

	def run_two_player(self):
		return 'two_player'

if __name__ == "__main__":
    game = Game(title, size)
    game.new()

