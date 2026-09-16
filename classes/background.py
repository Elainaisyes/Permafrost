import pygame

class Background (pygame.sprite.Sprite):
    def __init__(self, x, y, background_width, background_height, image, window):
        super().__init__()
        self.background = pygame.image.load(f'assets/images/Window_Background/{image}').convert_alpha()
        self.rect = pygame.Rect(x, y, background_width, background_height)
        self.background = pygame.transform.smoothscale(self.background, (background_width, background_height))
        self.window = window

    def draw(self):
        self.window.blit(self.background, self.rect)
    