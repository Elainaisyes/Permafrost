import pygame, math

class Particle (pygame.sprite.Sprite):

    def __init__(self, x, y, radius, angle_direction, speed, decay_rate, color, *groups):
        super().__init__(*groups)
        self.posX = float(x)
        self.posY = float(y)
        self.current_radius = radius
        # negative so it follows the unit circle
        self.angle_direction = -angle_direction
        self.speed = speed
        self.decay_rate = decay_rate
        self.color = color
        self.build_image()

    def build_image(self):
        diameter = max(1, int(self.current_radius * 2)) 
        self.image = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (diameter // 2, diameter // 2), max(1, int(self.current_radius)))
        self.rect = self.image.get_rect(center=(round(self.posX), round(self.posY)))

    def move(self):
        dx = math.cos(math.radians(self.angle_direction))
        dy = math.sin(math.radians(self.angle_direction))
        self.posX += dx * self.speed
        self.posY += dy * self.speed
        self.rect.center = (round(self.posX), round(self.posY))

    def loop(self):
        self.move()
        self.current_radius -= 0.01*self.decay_rate
        if (self.current_radius <= 0.5):
            self.kill()
            return
        self.build_image()

    def draw(self, window):
        window.blit(self.image, self.rect)