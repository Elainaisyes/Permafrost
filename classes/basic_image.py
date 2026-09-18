import pygame

class Basic_Image(pygame.sprite.Sprite):
    def __init__(self, image, x, y, width, height, scale_factor, window, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=(x,y))
        self.window = window

        if scale_factor > 1:
            self.image = pygame.transform.smoothscale(self.image, (width * scale_factor, height * scale_factor))
            
    def draw(self):
        self.window.blit(self.image, self.rect)