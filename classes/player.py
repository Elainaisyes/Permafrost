import pygame, random
from classes.particle import Particle

from load_sprite_sheets import load_sprite_sheets

class Player(pygame.sprite.Sprite):
    ANIMATION_DELAY = 3
    BASE_SPEED = 5

    # Sprite rows
    IDLE_FORWARDS = "Cirno_row0_"
    IDLE_FORWARDS_TURNED = "Cirno_row1_"
    IDLE_BACKWARDS = "Cirno_row4_"
    IDLE_BACKWARDS_TURNED = "Cirno_row3_"
    MOVING = "Cirno_row2_"
    FLY_UP = "Cirno_row1_"
    FLY_DOWN = "Cirno_row3_"

    def __init__(self, x, y):
        super().__init__()
        self.sprites = load_sprite_sheets("Cirno")
        self.image = self.sprites[f"{self.IDLE_FORWARDS}right"][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.x_velocity, self.y_velocity = 0, 0
        self.mask = None
        self.direction = "right"
        self.animation_count = 0
        self.speed = 5

        self.angle_direction = 90

        # Used to set sprite positions
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False
        self.looking_straight = True
        self.looking_backwards = False

        self.particles = pygame.sprite.Group()

    def move (self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def set_direction(self, dir):
        self.looking_straight = False
        if (self.direction != dir):
            if self.direction is not None and self.direction != dir:
                self.direction = dir
            self.animation_count = 0

    def handle_input (self):
        keys = pygame.key.get_pressed()
        self.x_velocity = 0
        self.y_velocity = 0
        self.moving_left = False
        self.moving_right = False
        self.moving_up = False
        self.moving_down = False

        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.speed = self.BASE_SPEED / 2
        else:
            self.speed = self.BASE_SPEED

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x_velocity = -self.speed
            self.set_direction('left')
            self.moving_left = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x_velocity = self.speed
            self.set_direction('right')
            self.moving_right = True


        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y_velocity = -self.speed
            self.moving_up = True

            self.looking_straight = True
            self.looking_backwards = False

        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y_velocity = self.speed
            self.moving_down = True
            self.looking_straight = True
            self.looking_backwards = True


    def loop(self):
        self.move(self.x_velocity, self.y_velocity)
        self.handle_input()
        self.update_sprite()
        for i in range(1,5):
            Particle(self.rect.centerx, self.rect.centery,
                    random.randint(10,40)/10, -self.angle_direction, 
                    random.randint(10,30)/10, random.randint(10,50)/10, 
                    (255,255,255), self.particles)
            
        for particle in self.particles:
            particle.loop()

    def update_sprite(self):
        if self.looking_straight:
            idle_type = self.IDLE_FORWARDS
            self.angle_direction = 90
        else:
            idle_type = self.IDLE_FORWARDS_TURNED
            self.angle_direction = 45 if self.direction == "right" else 135

        if self.looking_backwards:
            if self.looking_straight:
                idle_type = self.IDLE_BACKWARDS
                self.angle_direction = -90
            else:
                idle_type = self.IDLE_BACKWARDS_TURNED
                self.angle_direction = -45 if self.direction == "right" else -135
                    
        sprites = self.sprites[f"{idle_type}{self.direction}"]
        if self.x_velocity != 0:
            sprites = self.sprites[f"{self.MOVING}{self.direction}"]
            
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites) // 2
        self.animation_count += 1
        self.image = sprites[sprite_index]

        if ((self.moving_right or self.moving_left) and self.moving_up):
            self.image = self.sprites[f"{self.FLY_UP}{self.direction}"][4]

        if ((self.moving_right or self.moving_left) and self.moving_down):
            self.image = self.sprites[f"{self.FLY_DOWN}{self.direction}"][4]


        

    def draw(self, window):
        for particle in self.particles:
            particle.draw(window)
        window.blit(self.image, self.rect)