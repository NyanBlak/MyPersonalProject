import pygame

size = WIDTH, HEIGHT = 600, 600
FPS = 60


class Game:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Chess!")
        self.screen = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()
        self.running = True

    def new(self):
        self.run()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.events()
            pygame.display.flip()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False


def main():
    game = Game()
    game.new()

if __name__ == "__main__":
    main()