import pygame

class Basic_Image(pygame.sprite.Sprite):
    def __init__(self, image, x, y, width, height, scale_factor, window, *groups, color=None, alpha=255, rotation_angle=0):
        super().__init__(*groups)
        self.original_image = image
        self.image = image
        self.window = window
        self.x_pos = float(x)
        self.y_pos = float(y)
        self.alpha = alpha
        self.scale_factor = scale_factor
        self.rotation_angle = rotation_angle

        if scale_factor > 0:
            self.image = pygame.transform.smoothscale(self.image, (width * scale_factor, height * scale_factor))

        if rotation_angle != 0:
            self.image = pygame.transform.rotate(self.image, rotation_angle)

        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect(topleft=(self.x_pos,self.y_pos))

        if color is not None:
            tinted = self.image.copy()
            alpha = color[3] if len(color) > 3 else 255
            tinted.fill((*color[:3], alpha), special_flags=pygame.BLEND_RGBA_MULT)
            self.image = tinted
            
    def draw(self):
        self.window.blit(self.image, self.rect)