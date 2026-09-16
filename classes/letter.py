import pygame
from util.load_sprite_sheets import load_sprite_sheets

class Letter(pygame.sprite.Sprite):
    def __init__(self, image, x, y, size, scale_factor, window, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=(x,y))
        self.image = pygame.transform.smoothscale(self.image, (size * scale_factor, size * scale_factor))
        self.window = window

    def draw(self):
        self.window.blit(self.image, self.rect)