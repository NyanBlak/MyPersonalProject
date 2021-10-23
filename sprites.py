import pygame as pg
import os

pg.font.init()
FONT = pg.font.SysFont(None, 16)

path = "".join(os.path.split(__file__)[:-1])

IMAGE_NORMAL = pg.image.load(os.path.join(path, "Images", "normal.png"))
IMAGE_HOVER = pg.image.load(os.path.join(path, "Images", "hover.png"))
IMAGE_DOWN = pg.image.load(os.path.join(path, "Images", "down.png"))

class Button(pg.sprite.Sprite):

    def __init__(self, x, y, width, height, callback, text='',
        text_color=(0,0,0), font=FONT, image_normal=IMAGE_NORMAL,
        image_down=IMAGE_DOWN, image_hover=IMAGE_HOVER, val=-1):
        super().__init__()

        self.val = val
        self.image_normal = pg.transform.scale(image_normal, (width, height))
        self.image_hover = pg.transform.scale(image_hover, (width, height))
        self.image_down = pg.transform.scale(image_down, (width, height))

        self.image = self.image_normal  # The currently active image.
        self.rect = self.image.get_rect(topleft=(x, y))
        self.text = text

        # To center the text rect.
        image_center = self.image.get_rect().center
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=image_center)

        # Blit the text onto the images.
        for image in (self.image_normal, self.image_hover, self.image_down):
            image.blit(text_surf, text_rect)

        # This function will be called when the button gets pressed.
        self.callback = callback
        self.button_down = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.image = self.image_down
                self.button_down = True
        elif event.type == pg.MOUSEBUTTONUP:
            # If the rect collides with the mouse pos.
            if self.rect.collidepoint(event.pos) and self.button_down:
                self.callback()  # Call the function.
                self.image = self.image_hover
            self.button_down = False
        elif event.type == pg.MOUSEMOTION:
            collided = self.rect.collidepoint(event.pos)
            if collided and not self.button_down:
                self.image = self.image_hover
            elif not collided:
                self.image = self.image_normal
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
