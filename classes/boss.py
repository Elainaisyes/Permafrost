import pygame, math, random
from classes.basic_image import Basic_Image
from classes.particle import Particle
from classes.boss_bullet import Boss_Bullet
from util.load_sprite_sheets import load_sprite_sheets, load_sprite_sheet_row
from util.play_sound import play_sound

def lerp(current, target, multiplier):
    return current + (target - current) * multiplier

def lerp_angle(current, target, multiplier):
    delta = (target - current) % 360
    # Helps decide whether to turn clockwise or counter-clockwise
    if delta > 180:
        delta -= 360
    elif delta < -180:
        delta += 360

    return current + delta * multiplier

class Phase:
    def __init__(self, health, timer, start_spellcard_health=None, is_spellcard=False, name=None):
        self.health = health
        self.start_spellcard_health = start_spellcard_health
        self.timer = timer
        self.is_spellcard = is_spellcard
        self.name = name

class Boss(pygame.sprite.Sprite):
    ANIMATION_DELAY = 4
    MAX_SPEED = 6
    SHOOT_DELAY = 4
    FPS = 60
    SPELLCARD_IMAGE_DELAY = 90

    # Sprite rows
    IDLE_FORWARDS = "Flandre_row0_"
    IDLE_FORWARDS_TURNED = "Flandre_row1_"
    IDLE_BACKWARDS = "Flandre_row4_"
    IDLE_BACKWARDS_TURNED = "Flandre_row3_"
    MOVING = "Flandre_row2_"

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

        self.player = player

        self.phases = (
            Phase(5000, 30, start_spellcard_health=3000),
            Phase(None, 60, is_spellcard=True, name='Taboo "Cranberry Trap"'),

            Phase(2000, 30, start_spellcard_health=3000),
            Phase(None, 60, is_spellcard=True, name='Taboo "Laevateinn"'),

            Phase(2000, 30, start_spellcard_health=4000),
            Phase(None, 60, is_spellcard=True, name='Taboo "Four of a Kind"'),

            Phase(2000, 30, start_spellcard_health=3000),
            Phase(None, 60, is_spellcard=True, name='Taboo "Kagome, Kagome"'),

            Phase(2000, 30, start_spellcard_health=3000),
            Phase(None, 60, is_spellcard=True, name='Taboo "Maze of Love"'),

            Phase(4000, 60, is_spellcard=True, name='Forbidden Barrage "Starbow Break"'),

            Phase(4000, 60, is_spellcard=True, name='Forbidden Barrage "Catadioptric"'),

            Phase(4000, 60, is_spellcard=True, name='Forbidden Barrage "Counter Clock"'),

            Phase(99999999, 60, is_spellcard=True, name='Secret Barrage "And Then Will there be None?"'),

            Phase(7000, 120, is_spellcard=True, name='Q.E.D. "Ripples of 495 Years"')
        )

        self.attacks_left = 9
        self.phase_health = 0
        self.health = self.phase_health
        self.phase_timer = 0
        self.phase_timer_delay = 0
        self.phase_index = 0
        self.phase = self.phases[self.phase_index]
        self.phase_time_elapsed = 0
        self.in_spellcard = False
        self.start_phase()

        self.spellcard_image_delay_over = False
        self.spellcard_image_delay_tick = 1

        #Used to set minimum speeds of the spiral bullets
        self.spiral_bullet_layer = 1

        self.bullet_sprites = load_sprite_sheet_row("Projectiles", 16, 16, 16, 9 + 16*4, 8, 1.25, "bullet")
        self.bullet_leftover_sprites = load_sprite_sheet_row("Projectiles", 16, 16, 16, 9 + 16*15, 8, 1.25, "leftover")
        self.bullets = pygame.sprite.Group()
        self.leftovers = pygame.sprite.Group()
        self.basic_attack_sfx = pygame.mixer.Sound("assets/audios/sfx/tan01.wav")


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
        self.spellcard_start_sfx = pygame.mixer.Sound("assets/audios/sfx/cat00.wav")
        
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

    def set_desired_position(self, x, y):
        self.desired_x = x
        self.desired_y = y

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
            self.health = max(0, round(self.health - player.damage))
            play_sound(self.boss_hurt_sfx,0.1)
            

        self.phase_timer_delay += 1
        if self.phase_timer_delay % self.FPS == 0:
            self.phase_timer -= 1
            if -1 < self.phase_timer < 10:
                play_sound(self.time_running_out_sfx, 0.75)

        # Need to avoid comparison by None errors
        check_start_health = False
        if self.phase.start_spellcard_health is not None:
            check_start_health = self.health <= self.phase.start_spellcard_health
            
        if self.phase_timer < 0 or self.health <= 0 or check_start_health:
            self.create_leftovers()
            if self.phase.name is not None:
                self.attacks_left -= 1
            self.phase_timer = self.phase.timer
            self.phase_index = (self.phase_index + 1) % len(self.phases)
            self.start_phase()

        if self.spellcard_image_delay_tick % self.SPELLCARD_IMAGE_DELAY != 0 and not self.spellcard_image_delay_over:
            self.spellcard_image_delay_tick += 1
        else:
            self.spellcard_image_delay_over = True

        self.boss_action(self.player)

        self.phase_time_elapsed += 1
        for bullet in self.bullets:
            bullet.loop()

        for leftover in self.leftovers:
            leftover.alpha = lerp(leftover.alpha, 0, 0.05)
            leftover.image.set_alpha(leftover.alpha)
            if leftover.alpha <= 0:
                leftover.kill()

        collider = player if not player.shift_down else player.shift_hitbox_marker
        if not player.invulnerable:
            boss_bullet_collided = pygame.sprite.spritecollide(collider, self.bullets, True, pygame.sprite.collide_mask)
            if boss_bullet_collided:
                player.health = max(0, player.health-1)
                play_sound(player.player_hit_sfx, 0.2)
                self.create_leftovers()
            else:
                for bullet in self.bullets:
                    offset = (bullet.rect.x - player.rect.x, bullet.rect.y - player.rect.y)                
                    if player.graze_mask.overlap(bullet.mask, offset) is not None and not bullet.graze_detected:
                        player.graze += 1
                        play_sound(player.graze_sfx, 0.25)
                        bullet.graze_detected = True

    def create_leftovers(self):
        for bullet in self.bullets: 
            Boss_Bullet(bullet.rect.centerx,bullet.rect.centery,self.bullet_leftover_sprites["Projectiles_leftover"][10], self.window, 0, 90, 255, bullet.image.get_width() / 24, "normal", 2.5, self.leftovers)
        self.bullets.empty()

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
        self.phase = self.phases[self.phase_index]
        self.phase_time_elapsed = 0
        
        if self.phase.is_spellcard:
            self.in_spellcard = True
            play_sound(self.spellcard_start_sfx, 0.5)
        else:
            self.in_spellcard = False
        print(self.phase.name or "Basic_Attack", self.phase_index)

        if self.phase.health is not None:
            self.phase_health = self.phase.health
            self.health = self.phase.health
        

        self.phase_timer = self.phase.timer
        self.phase_timer_delay = 0
        self.phase_time_elapsed = 0

        self.spellcard_image_delay_over = False
        self.spellcard_image_delay_tick = 1

    def boss_action(self, player):
        # When checking for time elasped, need to make sure only to use increments of 0.05, anything else may not fulfill checking requirements due to floating point decimals
        time_elapsed = self.phase_time_elapsed / 60

        for bullet in self.bullets:
            if bullet.type == "spiral":
                bullet.speed = lerp(bullet.speed, bullet.minimum_speed, 0.2)

        for bullet in self.bullets:
            if bullet.rect.top > 750 or bullet.rect.bottom < 0 or bullet.rect.right < 0 or bullet.rect.left > self.screen_width:
                bullet.kill()

        if self.phase_index == 0:
            cycle_frame = self.phase_time_elapsed % 60
            # First Basic Attack
            if cycle_frame == 0:
                play_sound(self.basic_attack_sfx, 0.125)
                self.spiral_bullet_layer = 1
                self.first_volley_pos = self.rect.centerx-8, self.rect.centery-8
            if cycle_frame in {0, 1}:
                x, y = self.first_volley_pos
                self.spiral_pattern(x, y, 360 / 32, 0, 3 - 0.5*(self.spiral_bullet_layer-1), 1.25)
                self.spiral_bullet_layer += 1
            if self.phase_time_elapsed % 120 == 0:
                self.set_desired_position(random.randint(0,400), random.randint(75,150))

        if self.phase_index == 12:
            # Basic attack before Catadiotropic
            cycle_frame = self.phase_time_elapsed % 30
            if cycle_frame == 0:
                play_sound(self.basic_attack_sfx, 0.125)
                self.spiral_bullet_layer = 1
                self.first_volley_pos = self.rect.centerx-8, self.rect.centery-8
            if cycle_frame in {0, 3, 6}:
                x, y = self.first_volley_pos
                self.spiral_pattern(x, y, 360 / 32, cycle_frame*2/3, 2.5 + 0.5*(self.spiral_bullet_layer-1), 1, 6)
                self.spiral_bullet_layer += 1

            if self.phase_time_elapsed % 90 == 0:
                self.set_desired_position(random.randint(100,300), random.randint(75,150))

    def spiral_pattern(self, x, y, spiral_pattern_angle, angle_offset=0, minimum_speed=2.5, scale=1, color_index=1):
        bullet_count = math.floor(360 / spiral_pattern_angle)
        angle_step = 360 / bullet_count

        for i in range(bullet_count):
            Boss_Bullet(x, y, self.bullet_sprites["Projectiles_bullet"][color_index],self.window, 15, 90 - i * angle_step + angle_offset, 255, scale, "spiral", minimum_speed, self.bullets,)

    def draw(self):
        self.particles.draw(self.window)
        self.window.blit(self.image, self.rect)
        self.bullets.draw(self.window)
        self.leftovers.draw(self.window)