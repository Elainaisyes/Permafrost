import pygame
from classes.basic_image import Basic_Image
from util.load_sprite_sheets import load_sprite_sheets

class Letter(Basic_Image):
    def __init__(self, image, x, y, width, height, scale_factor, color, window, *groups):
        super().__init__(image, x, y, width, height, scale_factor, window, *groups)

        if color is not None:
            tinted = self.image.copy()
            tinted.fill((*color[:3], 255), special_flags=pygame.BLEND_RGBA_MULT)
            self.image = tinted
            