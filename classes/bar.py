import pygame

class Bar(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, window, *groups, border_radius=5, has_border=False, border_color=None, 
                 is_gradient=False, gradient_start_color=None, gradient_end_color=None, max_width=None, max_height=None, vertical=False):
        super().__init__(*groups)
        self.x_pos = x
        self.y_pos = y
        self.width = width
        self.height = height
        self.color = color
        self.border_radius = border_radius
        self.has_border = has_border
        self.border_color = border_color
        self.is_gradient = is_gradient
        self.gradient_start_color = gradient_start_color
        self.gradient_end_color = gradient_end_color
        self.window = window
        self.max_width = max_width
        self.max_height = max_height
        if self.max_width is None:
            self.max_width = width
        if self.max_height is None:
            self.max_height = height
        self.vertical = vertical
        self.build_image()

        self.default_color = color
        self.default_border_radius = border_radius
        self.default_has_border = has_border
        self.default_border_color = border_color
        self.default_is_gradient = is_gradient
        self.default_gradient_start_color = gradient_start_color
        self.default_gradient_end_color = gradient_end_color

    def build_image(self):
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(self.x_pos,self.y_pos))

        
        if not self.is_gradient:
            pygame.draw.rect(self.image, (self.color[:3]), (0, 0, self.width, self.height), border_radius=self.border_radius)
        else:
            gradient = pygame.Surface((self.max_width, self.height), pygame. SRCALPHA)
            if not self.vertical:
                for x in range(self.max_width):
                    interpolation = x / max(1, self.max_width - 1)
                    r,g,b = self.get_line_rgb(interpolation)
                    pygame.draw.line(gradient, (r, g, b), (x, 0), (x, self.height))
            else:
                gradient = pygame.Surface((self.width, self.max_height), pygame. SRCALPHA)
                for y in range(self.max_height):
                    interpolation = y / max(1, self.max_height - 1)
                    r,g,b = self.get_line_rgb(interpolation)
                    pygame.draw.line(gradient, (r, g, b), (0, y), (self.width, y))

            mask = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, self.width, self.height), border_radius=self.border_radius)
            gradient.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.image.blit(gradient, (0, 0))

        if self.has_border and self.border_color is not None:
            pygame.draw.rect(self.image, (self.border_color[:3]), (0, 0, self.width, self.height), border_radius=self.border_radius, width=2)


    def get_line_rgb(self, interpolation):
        r = int(self.gradient_start_color[0] + (self.gradient_end_color[0] - self.gradient_start_color[0]) * interpolation)
        g = int(self.gradient_start_color[1] + (self.gradient_end_color[1] - self.gradient_start_color[1]) * interpolation)
        b = int(self.gradient_start_color[2] + (self.gradient_end_color[2] - self.gradient_start_color[2]) * interpolation)
        return (r,g,b)
    def draw(self):
        self.window.blit(self.image, self.rect)