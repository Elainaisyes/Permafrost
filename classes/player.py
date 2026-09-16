import pygame, random, math
from classes.particle import Particle
from classes.player_bullet import Player_Bullet
from load_sprite_sheets import load_sprite_sheet_row, load_sprite_sheets

def lerp(start, end, multiplier):
    return start + (end - start) * multiplier

class Player(pygame.sprite.Sprite):
    ANIMATION_DELAY = 3
    BASE_SPEED = 4
    SHOOT_DELAY = 4

    # Sprite rows
    IDLE_FORWARDS = "Cirno_row0_"
    IDLE_FORWARDS_TURNED = "Cirno_row1_"
    IDLE_BACKWARDS = "Cirno_row4_"
    IDLE_BACKWARDS_TURNED = "Cirno_row3_"
    MOVING = "Cirno_row2_"
    FLY_UP = "Cirno_row1_"
    FLY_DOWN = "Cirno_row3_"


    def __init__(self, x, y, window, screen_width=600):
        super().__init__()
        self.sprites = load_sprite_sheets("Cirno", 24, 32, 8, 2, "right")
        self.image = self.sprites[f"{self.IDLE_FORWARDS}right"][0]
        self.x_pos = float(x)
        self.y_pos = float(y)
        self.rect = self.image.get_rect(topleft=(self.x_pos, self.y_pos))
        self.x_velocity, self.y_velocity = 0, 0
        self.mask = None
        self.direction = "right"
        self.animation_count = 0
        self.speed = self.BASE_SPEED
        self.alpha = 255

        self.window = window
        self.screen_width = screen_width

        self.angle_direction = 90

        # Used to set sprite positions
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False
        self.looking_straight = True
        self.looking_backwards = False
        
        self.shift_down = False

        self.particles = pygame.sprite.Group()
        self.particle_offset_y = 22

        self.bullets = pygame.sprite.Group()
        self.bullet_sprites = load_sprite_sheet_row("Projectiles", 16, 16, 16, 9 + 16*4, 8, 1.25, "bullet")
        self.big_bullet_sprites = load_sprite_sheet_row("Projectiles", 32, 32, 8, 9 + 16 * 7, 8, 1, "big_bullet")
        self.marker_sprites = load_sprite_sheet_row("Projectiles", 16, 16, 16, 9 + 16*3, 8, 0.7, "marker")
        self.shoot_count = self.SHOOT_DELAY-1
        self.bullet_offset = 16

        self.shift_hitbox_marker = Player_Bullet(self.rect.centerx-10, self.rect.centery-10, 
                                                 self.marker_sprites["Projectiles_marker"][7], self.window,
                                                 0, False, False)
        
        self.left_big_bullet = Player_Bullet(self.rect.centerx - self.bullet_offset - 24, self.rect.centery - 48,
                                             self.big_bullet_sprites["Projectiles_big_bullet"][4], self.window,
                                             0, False, True, self.bullets)
        self.right_big_bullet = Player_Bullet(self.rect.centerx + self.bullet_offset, self.rect.centery - 48, 
                                              self.big_bullet_sprites["Projectiles_big_bullet"][4], self.window,
                                              0, False, True, self.bullets)

    def move (self, dx, dy):            
        self.x_pos += dx
        self.y_pos += dy

        bullet_width, bullet_height = (self.big_bullet_sprites["Projectiles_big_bullet"][4].get_size())

        min_x = self.bullet_offset + bullet_width/2 - self.rect.width//2 + 8
        max_x = (self.screen_width - self.bullet_offset - 12
                  - bullet_width/2 - self.rect.width//2)

        self.x_pos = max(min(self.x_pos, max_x), min_x)
        self.y_pos = max(min(self.y_pos, self.window.height - self.rect.height/2
                               + 48 - bullet_height), 28)
        
        self.rect.x = round(self.x_pos)
        self.rect.y = round(self.y_pos)

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
        speed = self.BASE_SPEED
        self.shift_down = False
        

        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            speed /= 1.6
            self.shift_down = True
        
        if (self.moving_right or self.moving_left) and (self.moving_up or self.moving_down):
            # Equalizes diagnol movement
            speed *= math.sqrt(2)/2

        self.speed = speed

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


        desired_bullet_offset = 16 if not self.shift_down else 4
        self.bullet_offset = lerp(self.bullet_offset, desired_bullet_offset, 0.2)
        if keys[pygame.K_SPACE] or keys[pygame.K_z]:
            self.shoot_count += 1
            if self.shoot_count % self.SHOOT_DELAY == 0:
                Player_Bullet(self.rect.centerx-self.bullet_offset-22, self.rect.centery - 48,
                               self.bullet_sprites["Projectiles_bullet"][7], self.window,
                               10, True, True, self.bullets)
                Player_Bullet(self.rect.centerx+self.bullet_offset+2, self.rect.centery - 48,
                               self.bullet_sprites["Projectiles_bullet"][7], self.window,
                               10, True, True, self.bullets)



    def loop(self):
        self.handle_input()
        self.move(self.x_velocity, self.y_velocity)
        self.update_sprite()
        desired_alpha = 200 if self.shift_down else 255
        self.alpha = lerp(self.alpha, desired_alpha, 0.2)
        self.image.set_alpha(self.alpha)
        for i in range(1,5):
            Particle(self.rect.centerx, self.rect.centery + self.particle_offset_y,
                    random.randint(10,40)/10, -self.angle_direction + random.randint(-20,20), 
                    random.randint(10,30)/10 * self.speed / self.BASE_SPEED, random.randint(120,240)/10, 
                    (255,255,255), self.particles)
            
        for particle in self.particles:
            particle.alpha = self.alpha
            particle.loop()
        
        self.left_big_bullet.rect.centerx = self.rect.centerx - self.bullet_offset - 24 + 12
        self.right_big_bullet.rect.centerx = self.rect.centerx + self.bullet_offset + 24 - 12
        self.left_big_bullet.rect.centery, self.right_big_bullet.rect.centery = self.rect.centery - 48, self.rect.centery - 48

        for bullet in self.bullets:
            if not bullet.damaging and bullet.create_particles:
                bullet.image.set_alpha(self.alpha)
            bullet.loop()
        self.shift_hitbox_marker.loop()
        self.shift_hitbox_marker.rect.centerx = self.rect.centerx
        self.shift_hitbox_marker.rect.centery = self.rect.centery
        hitbox_desired_alpha = 0 if not self.shift_down else 255
        hitbox_alpha = self.shift_hitbox_marker.image.get_alpha()
        self.shift_hitbox_marker.image.set_alpha(lerp(hitbox_alpha, hitbox_desired_alpha, 0.15))

    def update_sprite(self):
        if self.looking_straight:
            idle_type = self.IDLE_FORWARDS
            self.angle_direction = 90
            self.particle_offset_y = 0
        else:
            idle_type = self.IDLE_FORWARDS_TURNED
            self.angle_direction = 135 if self.direction == "right" else 45
            self.particle_offset_y = 18

        if self.looking_backwards:
            if self.looking_straight:
                idle_type = self.IDLE_BACKWARDS
                self.angle_direction = -90
                self.particle_offset_y = 0
            else:
                idle_type = self.IDLE_BACKWARDS_TURNED
                self.angle_direction = -135 if self.direction == "right" else -45

                    
        sprites = self.sprites[f"{idle_type}{self.direction}"]
        if self.x_velocity != 0:
            sprites = self.sprites[f"{self.MOVING}{self.direction}"]
            self.angle_direction = 0 if self.direction == "right" else 180
            
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites) // 2
        self.animation_count += 1
        self.image = sprites[sprite_index]

        if ((self.moving_right or self.moving_left) and self.moving_up):
            self.image = self.sprites[f"{self.FLY_UP}{self.direction}"][4]
            self.angle_direction = 135 if self.direction == "right" else 45
            self.particle_offset_y = 9

        if ((self.moving_right or self.moving_left) and self.moving_down):
            self.image = self.sprites[f"{self.FLY_DOWN}{self.direction}"][4]
            self.angle_direction = -135 if self.direction == "right" else -45
            self.particle_offset_y = 9

    def draw(self):
        self.particles.draw(self.window)

        for bullet in sorted(self.bullets, key=lambda s: s.rect.bottom):
            bullet.draw(self.window)

        self.window.blit(self.image, self.rect)
        self.shift_hitbox_marker.draw(self.window)