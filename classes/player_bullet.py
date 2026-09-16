import pygame, random
from classes.particle import Particle
from load_sprite_sheets import load_sprite_sheet_row

class Player_Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, image, window, y_velocity = 10, damaging = True, create_particles=True, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = None
        self.y_velocity = y_velocity
        self.damaging = damaging
        self.create_particles = create_particles

        self.window = window

        self.particles = pygame.sprite.Group()

    def loop(self):
        keys = pygame.key.get_pressed()
        self.rect.y -= self.y_velocity
        speed_multiplier = 1 if not keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else 0.5
        if self.create_particles:
            if self.damaging:
                Particle(self.rect.centerx, self.rect.centery, random.randint(10,40)/10, 90 + random.randint(-20,20), 
                        random.randint(10,30)/10, random.randint(200,300)/10, (255,255,255), self.particles)
            else:
                for i in range(1, 5):
                    Particle(self.rect.centerx, self.rect.centery, random.randint(10,40)/10, random.randint(1,360), 
                            random.randint(10,20)/10 * speed_multiplier, random.randint(200,300)/10, (255,255,255), self.particles) 
        
            for particle in self.particles:
                particle.loop()
            
        if (self.rect.y <= -50 and self.damaging): 
            self.kill()

    
    def draw(self, window):
        if self.create_particles:
            self.particles.draw(window)
        window.blit(self.image, self.rect)

