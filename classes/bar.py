import pygame

class Bar(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, window, *groups, border_radius=5, has_border=False, border_color=None, is_gradient=False, gradient_start_color=None, gradient_end_color=None):
        super().__init__(*groups)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x,y))

        
        self.window = window
        if not is_gradient:
            pygame.draw.rect(self.image, (color[:3]), (0, 0, width, height), border_radius=border_radius)
        else:
            for x in range(width):
                interpolation = x / max(1, width - 1)
                r = int(gradient_start_color[0] + (gradient_end_color[0] - gradient_start_color[0]) * interpolation)
                g = int(gradient_start_color[1] + (gradient_end_color[1] - gradient_start_color[1]) * interpolation)
                b = int(gradient_start_color[2] + (gradient_end_color[2] - gradient_start_color[2]) * interpolation)
                pygame.draw.line(self.image, (r, g, b), (x, 0), (x, height))

        if has_border and border_color is not None:
            pygame.draw.rect(self.image, (border_color[:3]), (0, 0, width, height), border_radius=border_radius, width=1)

    def draw(self):
        self.window.blit(self.image, self.rect)