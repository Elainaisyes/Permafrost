import pygame
from math import cos, sin, radians

class Boss_Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, image: pygame.Surface, window, speed, angle=0, alpha=255, scale=1.0, type="normal", minimum_speed = 2.5, *groups):
        super().__init__(*groups)
        self.original_image = image
        self.image = image.copy()
        self.angle_direction = angle
        self.alpha = alpha
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.minimum_speed = minimum_speed
        self.window = window
        self.type = type
        self.scale = scale

        self.graze_detected = False

        #rotozooom instead of rotate to make the image come out smoother.
        self.image = pygame.transform.rotozoom(self.original_image, 90 - angle, scale)
        self.rect = self.image.get_rect(center=self.rect.center)

        self.x_pos = float(self.rect.centerx)
        self.y_pos = float(self.rect.centery)
        self.image.set_alpha(self.alpha)
        self.mask = pygame.mask.from_surface(self.image)
        self.particles = pygame.sprite.Group()

    def loop(self):
        dx = cos(radians(self.angle_direction))
        dy = sin(radians(self.angle_direction))
        self.x_pos += dx * self.speed
        self.y_pos += dy * self.speed
        self.rect.center = (round(self.x_pos), round(self.y_pos))

    def draw(self, window):
        window.blit(self.image, self.rect)