import pygame

class Basic_Image(pygame.sprite.Sprite):
    def __init__(self, image, x, y, width, height, scale_factor, window, *groups, color=None):
        super().__init__(*groups)
        self.image = image
        self.window = window
        self.x_pos = float(x)
        self.y_pos = float(y)

        if scale_factor > 0:
            self.image = pygame.transform.smoothscale(self.image, (width * scale_factor, height * scale_factor))

        self.rect = self.image.get_rect(topleft=(self.x_pos,self.y_pos))

        if color is not None:
            tinted = self.image.copy()
            alpha = color[3] if len(color) > 3 else 255
            tinted.fill((*color[:3], alpha), special_flags=pygame.BLEND_RGBA_MULT)
            self.image = tinted
            
    def draw(self):
        self.window.blit(self.image, self.rect)