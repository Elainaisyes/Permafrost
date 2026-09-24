import pygame, math, random
from classes.basic_image import Basic_Image
from classes.particle import Particle
from util.load_sprite_sheets import load_sprite_sheets
from util.play_sound import play_sound

def lerp_angle(current, target, multiplier):
    delta = (target - current) % 360
    # Helps decide whether to turn clockwise or counter-clockwise
    if delta > 180:
        delta -= 360
    elif delta < -180:
        delta += 360

    return current + delta * multiplier

class Phase:
    def __init__(self, health, timer, is_spellcard=False):
        self.health = health
        self.timer = timer
        self.is_spellcard = is_spellcard

class Boss(pygame.sprite.Sprite):
    ANIMATION_DELAY = 4
    MAX_SPEED = 6
    SHOOT_DELAY = 4
    FPS = 60

    # Sprite rows
    IDLE_FORWARDS = "Flandre_row0_"
    IDLE_FORWARDS_TURNED = "Flandre_row1_"
    IDLE_BACKWARDS = "Flandre_row4_"
    IDLE_BACKWARDS_TURNED = "Flandre_row3_"
    MOVING = "Flandre_row2_"

    PHASES = (
        Phase(1500, 30),
        # Placeholder
        Phase(2200, 45, True)
    )

    def __init__(self, x, y, window, player, screen_width = 600):
        super().__init__()
        self.sprites = load_sprite_sheets("Flandre", 24, 32, 8, 2.5, "right")
        self.image = self.sprites[f"{self.IDLE_BACKWARDS}right"][0]
        self.x_pos = float(x)
        self.y_pos = float(y)
        self.rect = self.image.get_rect(topleft=(self.x_pos, self.y_pos))
        self.mask = pygame.mask.from_surface(self.image)
        self.x_velocity, self.y_velocity = self.MAX_SPEED, self.MAX_SPEED
        self.animation_count = 0
        self.angle_direction = 270
        self.direction = "right"
        self.speed = self.MAX_SPEED
        self.screen_width = screen_width
        self.sprite_screen_center_x = (self.screen_width-self.rect.width/4)/2
        self.desired_x, self.desired_y = self.sprite_screen_center_x, 750/4

        self.attacks_left = 9
        self.phase_health = 0
        self.health = self.phase_health
        self.phase_timer = 0
        self.phase_timer_delay = 0
        self.phase_index = 0
        self.phase_time_elapsed = 0
        self.start_phase()

        self.window = window
        self.aura_sprite = pygame.image.load("assets/images/Aura/Aura.png")
        self.aura = Basic_Image(self.aura_sprite, self.rect.x, self.rect.y, 500, 500, 0.42, self.window, color=(255,88,88,188))
        self.aura.original_image = self.aura.image
        self.aura_rotation = 0
        self.aura_rotation_speed = 2

        self.particles = pygame.sprite.Group()
        self.particle_offset_y = 0

        self.time_running_out_sfx = pygame.mixer.Sound("assets/audios/sfx/timeout.wav")
        self.boss_hurt_sfx = pygame.mixer.Sound("assets/audios/sfx/plst00.wav")

    def move(self):
        target_x = self.desired_x - self.rect.centerx
        target_y = self.desired_y - self.rect.centery
        distance = math.hypot(target_x, target_y)

        if distance <= 1:
            self.rect.center = (self.desired_x, self.desired_y)
            self.x_pos, self.y_pos = self.rect.topleft
            self.x_velocity = self.y_velocity = 0
            self.angle_direction = lerp_angle(self.angle_direction, -90, 0.2)
            return

        desired_angle = math.degrees(math.atan2(-target_y, target_x))

        if distance <= 30:
            self.angle_direction = lerp_angle(self.angle_direction, -90, 0.2)
        else:
            self.angle_direction = lerp_angle(self.angle_direction, desired_angle, 0.25)

        easing = max(0.25, min(1.0, distance / 90.0))
        movement = self.speed * easing

        if distance <= movement:
            movement = distance
            return

        self.x_velocity = target_x / distance * movement
        self.y_velocity = target_y / distance * movement

        self.x_pos += self.x_velocity
        self.y_pos += self.y_velocity
        self.rect.topleft = (round(self.x_pos), round(self.y_pos))

    def loop(self, player):
        self.move()
        for particle in self.particles:
            particle.loop()

        for i in range(1,5):
            Particle(self.rect.centerx, self.rect.centery + self.particle_offset_y,
                    random.randint(10,40)/10, -self.angle_direction + random.randint(-20,20), 
                    random.randint(10,30)/10 * self.speed / self.MAX_SPEED, random.randint(120,240)/10, 
                    (255,138,138), self.particles)

        self.update_aura()
        self.update_sprites()

        player_bullet_collided = pygame.sprite.spritecollide(self, player.bullets, True, pygame.sprite.collide_mask)
        if player_bullet_collided:
            self.health = max(0, self.health-player.damage)
            play_sound(self.boss_hurt_sfx,0.1)
            

        self.phase_timer_delay += 1
        if self.phase_timer_delay % self.FPS == 0:
            self.phase_timer -= 1
            if -1 < self.phase_timer < 10:
                play_sound(self.time_running_out_sfx, 0.75)

        if self.phase_timer < 0: 
            self.attacks_left -= 1
            self.phase_timer = 30

    def update_aura(self):
        self.aura.image = pygame.transform.rotate(self.aura.original_image, self.aura_rotation)
        self.aura_rotation -= self.aura_rotation_speed
        old_center = self.aura.rect.center
        self.aura.rect = self.aura.image.get_rect(center=old_center)

        boss_center_x = self.x_pos + self.rect.width / 2
        boss_center_y = self.y_pos + self.rect.height / 2
        self.aura.rect.centerx = round(boss_center_x)
        self.aura.rect.centery = round(boss_center_y) 

    def update_sprites(self):
        sprites = self.sprites[f"{self.IDLE_BACKWARDS}{self.direction}"]

        angle = self.angle_direction % 360
        sector = int((angle + 22.5) // 45) % 8

        if sector in {1, 3, 5, 7}:
            self.particle_offset_y = 18
        elif sector in {2, 6}:
            self.particle_offset_y = 9
        else: 
            self.particle_offset_y = 0

        sprite_keys = [
            f"{self.MOVING}right",                # 0: right
            f"{self.IDLE_FORWARDS_TURNED}right",  # 1: up-right
            f"{self.IDLE_FORWARDS}right",         # 2: up
            f"{self.IDLE_FORWARDS_TURNED}left",   # 3: up-left
            f"{self.MOVING}left",                 # 4: left
            f"{self.IDLE_BACKWARDS_TURNED}left",  # 5: down-left
            f"{self.IDLE_BACKWARDS}right",        # 6: down
            f"{self.IDLE_BACKWARDS_TURNED}right", # 7: down-right
        ]

        sprites = self.sprites[sprite_keys[sector]]
            
            
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites) // 2
        self.animation_count += 1
        self.image = sprites[sprite_index]
        self.mask = pygame.mask.from_surface(self.image)

    def start_phase(self):
        phase = self.PHASES[self.phase_index]

        self.phase_health = phase.health
        self.health = phase.health
        self.phase_timer = phase.timer
        self.phase_timer_delay = 0
        self.phase_time_elapsed = 0



    def draw(self):
        self.particles.draw(self.window)
        self.window.blit(self.image, self.rect)