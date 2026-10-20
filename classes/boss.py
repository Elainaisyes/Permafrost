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

        self.window = window
        self.aura_sprite = pygame.image.load("assets/images/Aura/Aura.png")
        self.aura = Basic_Image(self.aura_sprite, self.rect.x, self.rect.y, 500, 500, 0.42, self.window, color=(255,88,88,188))
        self.aura.original_image = self.aura.image
        self.aura_rotation = 0
        self.aura_rotation_speed = 2

        self.phases = (
            Phase(5000, 30, start_spellcard_health=3000),
            Phase(None, 60, is_spellcard=True, name='Taboo "Cranberry Trap"'),

            Phase(5000, 30, start_spellcard_health=3000),
            Phase(None, 60, is_spellcard=True, name='Taboo "Laevateinn"'),

            Phase(6000, 30, start_spellcard_health=4000),
            Phase(None, 60, is_spellcard=True, name='Taboo "Four of a Kind"'),

            Phase(5000, 30, start_spellcard_health=3000),
            Phase(None, 60, is_spellcard=True, name='Taboo "Kagome, Kagome"'),

            Phase(5000, 30, start_spellcard_health=3000),
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

        self.bullet_sprites = load_sprite_sheet_row("Projectiles", 16, 16, 16, 9 + 16*4, 8, 1.25, "bullet")
        self.round_bullet_sprites = load_sprite_sheet_row("Projectiles", 16, 16, 16, 9 + 16*3, 8, 1, "round_bullet")
        self.bullet_leftover_sprites = load_sprite_sheet_row("Projectiles", 16, 16, 16, 9 + 16*15, 8, 1.25, "leftover")
        self.fog_sprites = load_sprite_sheet_row("Projectiles", 32, 32, 8, 9 + 32*6.5, 8, 1, "fog")
        self.beam_sprites = load_sprite_sheet_row("Projectiles", 16, 16, 8, 9 + 16*0, 8, 1, "beam")
        self.bullets = pygame.sprite.Group()
        self.leftovers = pygame.sprite.Group()
        self.higher_attack_sfx = pygame.mixer.Sound("assets/audios/sfx/tan00.wav")
        self.basic_attack_sfx = pygame.mixer.Sound("assets/audios/sfx/tan01.wav")
        self.sparkle_sfx = pygame.mixer.Sound('assets/audios/sfx/kira00.wav')
        self.beam_sfx = pygame.mixer.Sound('assets/audios/sfx/lazer00.wav')


        self.particles = pygame.sprite.Group()
        self.particle_offset_y = 0

        self.time_running_out_sfx = pygame.mixer.Sound("assets/audios/sfx/timeout.wav")
        self.boss_hurt_sfx = pygame.mixer.Sound("assets/audios/sfx/plst00.wav")
        self.spellcard_start_sfx = pygame.mixer.Sound("assets/audios/sfx/cat00.wav")

        #Used to set minimum speeds of the spiral bullets
        self.spiral_bullet_layer = 1

        self.cranberry_auras = pygame.sprite.Group()

        # Used for finding positions and bounds for the aura emitters in Cranberry Trap
        self.cranberry_aura_bounds = {
            "top": 12,
            "left": 12,
            "bottom": 750-12,
            "right": 600-12,
        }

        edge_positions = {
            "topright": (self.cranberry_aura_bounds["right"], self.cranberry_aura_bounds['top']),
            "topleft": (self.cranberry_aura_bounds["left"], self.cranberry_aura_bounds['top']),
            "bottomleft": (self.cranberry_aura_bounds["left"], self.cranberry_aura_bounds['bottom']),
            "bottomright": (self.cranberry_aura_bounds["right"], self.cranberry_aura_bounds['bottom']),
        }

        for index, (itr, (x, y)) in enumerate(zip(self.cranberry_aura_bounds, edge_positions.values())):
            aura = Boss_Bullet(0, 0, self.aura_sprite, self.window, 10, 0, 0, 0.21, "emitter", 0, self.cranberry_auras)
            aura.rect.center = (x, y)
            aura.edge = itr
            horizontal = (1, 0) if x == self.cranberry_aura_bounds["left"] else (-1, 0)
            vertical = (0, 1) if y == self.cranberry_aura_bounds["top"] else (0, -1)
            aura.direction = random.choice((horizontal, vertical))
            aura.frozen = False
            aura.frozen_timer = 0
            aura.frozen_wait_time = random.randint(20,60)
            aura.bullet_color_index = 6 if index % 2 == 0 else 4
            aura.activation_priority = 1 if index % 2 == 1 else 2
            aura.can_shoot = True
            aura.activation_timer = 0
            aura.activation_threshold = 120


        for cranberry_aura in self.cranberry_auras:
            tinted = cranberry_aura.image.copy()
            tinted.fill((255,88,88,255), special_flags=pygame.BLEND_RGBA_MULT)
            cranberry_aura.image = tinted

        self.fogs = pygame.sprite.Group()
        self.beams = pygame.sprite.Group()
        # Boss_Bullet(200, 200, self.fog_sprites["Projectiles_fog"][1], self.window, 10, 0, 255, 2, "fog", 0, self.fogs)
        self.shooting_beams = True
        self.last_shooting_beams = False
        self.beam_state = "SWEEP"
        self.beam_direction = 1
        self.beam_angle = -165
        self.beam_angle_start_set = False
        self.first_sweep = True
        
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
            if self.health >= 0 and self.phase.is_spellcard:
                play_sound(pygame.mixer.Sound('assets/audios/sfx/cat00.wav'))

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
            if leftover.alpha <= 1:
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

        for beam in self.beams:
            beam.width = lerp(beam.width, 0, 0.15)
            self.update_beam(beam)
            if beam.width <= 5:
                beam.kill()

        for bullet in self.bullets:
            if bullet.rect.top > 750+100 or bullet.rect.bottom < 0-100 or bullet.rect.right < 0-100 or bullet.rect.left > self.screen_width+100:
                bullet.kill()

        if self.phase_index == 1:
            # First Basic Attack
            if time_elapsed >= 1:
                self.spiral_attack(1, 32, 3, {0, 1}, True, 0.5, 0, 1.25, 1)

            if self.phase_time_elapsed % 120 == 0:
                self.set_desired_position(random.randint(100,500), random.randint(75,150))

        if self.phase_index == 1:
            # Taboo Cranberry Trap
            cycle_frame = self.phase_time_elapsed % 12

            if time_elapsed == 0:
                self.set_desired_position(300, 100)

            if self.phase_time_elapsed % 150 == 0 and self.phase_time_elapsed > 0:
                self.set_desired_position(random.randint(200,400), random.randint(75,150))

            if time_elapsed >= 1:
                for aura in self.cranberry_auras:
                    if aura.activation_priority == 1:
                        aura.alpha = lerp(aura.alpha, 188, 0.1)
                        if aura.alpha >= 187: 
                            aura.alpha = 188
                        aura.image.set_alpha(aura.alpha)

                    if aura.alpha < 188:
                        continue

                    aura.activation_timer += 1
                    if aura.activation_timer % aura.activation_threshold == 0:
                        if aura.can_shoot:
                            aura.activation_threshold = 45
                        else:
                            aura.activation_threshold = 150

                        aura.can_shoot = not aura.can_shoot


                    if aura.frozen:
                        aura.frozen_timer += 1
                        if aura.frozen_timer >= aura.frozen_wait_time:
                            aura.frozen_timer = 0
                            aura.frozen = False
                    else:
                        aura.speed = lerp(aura.speed, 5, 0.02)
                    self.move_aura_emitter(aura, aura.speed)                     
                    if cycle_frame == 0 and aura.can_shoot:
                        dx, dy = aura.direction
                        offset_x, offset_y = 36 * dx, 36 * dy
                        if aura.bullet_color_index == 6:
                            play_sound(self.basic_attack_sfx, 0.0625)
                            Boss_Bullet(aura.rect.centerx + offset_x, aura.rect.centery + offset_y, self.round_bullet_sprites["Projectiles_round_bullet"][aura.bullet_color_index], self.window, 2.5, math.degrees(math.atan2(player.shift_hitbox_marker.rect.centery-aura.rect.centery, player.shift_hitbox_marker.rect.centerx-aura.rect.centerx)), 255, 1.5, "normal", 5, self.bullets)
                        else:
                            play_sound(self.sparkle_sfx, 0.2)
                            Boss_Bullet(aura.rect.centerx + offset_x, aura.rect.centery + offset_y, self.round_bullet_sprites["Projectiles_round_bullet"][aura.bullet_color_index], self.window, 2.5, math.degrees(math.atan2(750//2-aura.rect.centery, 600//2-aura.rect.centerx)), 255, 1.5, "normal", 5, self.bullets)

            if time_elapsed >= 10:
              for aura in self.cranberry_auras:
                    if aura.activation_priority == 2:
                        aura.alpha = lerp(aura.alpha, 188, 0.1)
                        if aura.alpha >= 187: 
                            aura.alpha = 188
                        aura.image.set_alpha(aura.alpha)
        elif self.phase_index == 2:
            for aura in self.cranberry_auras:
                aura.alpha = lerp(aura.alpha, 0, 0.1)
                aura.image.set_alpha(aura.alpha)

        if self.phase_index == 2:
            # Basic attack before Laevateinn
            if time_elapsed >= 1.5:
                self.spiral_attack(0.5, 32, 3, {0,1}, True, 0.5, 0, 1.25, 1)

            if self.phase_time_elapsed % 120 == 0:
                self.set_desired_position(random.randint(200,400), random.randint(75,150))

        if self.phase_index == 0:
            # Taboo Laevateinn
            beam_cycle_frame = self.phase_time_elapsed % 2
            bullet_cycle_frame = self.phase_time_elapsed % 5

            if self.last_shooting_beams is not self.shooting_beams:
                if self.shooting_beams:
                    play_sound(self.beam_sfx, 0.2)
                self.last_shooting_beams = self.shooting_beams

            if self.beam_state == "SWEEP":
                self.create_beam(beam_cycle_frame, self.beam_angle)
                if bullet_cycle_frame == 0 and self.shooting_beams:
                    play_sound(self.basic_attack_sfx, 0.1)
                    Boss_Bullet(self.rect.centerx, self.rect.centery, self.bullet_sprites["Projectiles_bullet"][1], self.window, 2.5, self.beam_angle+90, 255, 1.25, "normal", 2.5, self.bullets)
                    for i in range(0, 750//100):
                        spawn_distance = 100*i
                        beam_origin = self.beams.sprites()[-1].start_pos if self.beams else self.rect.center
                        beam_dir_x = math.cos(math.radians(self.beam_angle))
                        beam_dir_y = math.sin(math.radians(self.beam_angle))
                        spawn_x = beam_origin[0] + beam_dir_x * spawn_distance
                        spawn_y = beam_origin[1] + beam_dir_y * spawn_distance
                        Boss_Bullet(spawn_x, spawn_y, self.bullet_sprites["Projectiles_bullet"][1], self.window, 2.5, self.beam_angle+90, 255, 1.25, "normal", 2.5, self.bullets)
                if self.beam_direction == -1:
                    #Counterclockwise
                    self.beam_sweep(345, 85)
                else:
                    self.beam_sweep(195, 95)
                    

            if self.phase_time_elapsed % 30 and 2 > self.phase_time_elapsed > 0:
                self.set_desired_position(300, 100)

        if self.phase_index == 12:
            # Basic attack before Catadiotropic
            if time_elapsed >= 1:
                self.spiral_attack(0.5, 32, 2.5, {0, 3, 6}, True, -0.5, 2/3, 1, 6)

            if self.phase_time_elapsed % 90 == 0:
                self.set_desired_position(random.randint(100,500), random.randint(75,150))

    def spiral_pattern(self, x, y, spiral_pattern_angle, angle_offset=0, minimum_speed=2.5, scale=1, color_index=1, aimed_angle=None):
        bullet_count = math.floor(360 / spiral_pattern_angle)
        angle_step = 360 / bullet_count
        base_angle = aimed_angle if aimed_angle is not None else 90 + angle_offset

        for i in range(bullet_count):
            angle = base_angle - i * angle_step
            Boss_Bullet(x, y, self.bullet_sprites["Projectiles_bullet"][color_index],self.window, 15, angle, 255, scale, "spiral", minimum_speed, self.bullets,)

    def spiral_attack(self, shoot_speed, bullet_count = 32, top_speed = 3, bullet_count_set={0}, use_first_volley_pos=True, bullet_speed_difference = 0.5, bullet_angle_offset_multiplier=2/3, scale=1, color_index=1, target_player = False):
        cycle_frame = self.phase_time_elapsed % (shoot_speed * 60)

        target_x, target_y, = self.player.shift_hitbox_marker.rect.center
        aimed_angle = None
        if target_player:
            target_x, target_y = self.player.shift_hitbox_marker.rect.center
            aimed_angle = math.degrees(math.atan2(target_y - self.rect.centery, target_x - self.rect.centerx))
        if cycle_frame == 0:
            play_sound(self.basic_attack_sfx, 0.125)
            self.spiral_bullet_layer = 1
            self.first_volley_pos = self.rect.centerx-8, self.rect.centery-8
        if cycle_frame in bullet_count_set:
            if use_first_volley_pos:
                x, y = self.first_volley_pos
            else:
                x, y = self.rect.centerx - 8, self.rect.centery
                
            angle_offset = cycle_frame * bullet_angle_offset_multiplier if bullet_angle_offset_multiplier != 0 else 0
            self.spiral_pattern(x, y, 360 / bullet_count, angle_offset, top_speed - bullet_speed_difference*(self.spiral_bullet_layer-1), scale, color_index, aimed_angle)
            self.spiral_bullet_layer += 1


    def move_aura_emitter(self, aura, speed):
        bounds = self.cranberry_aura_bounds
        dx, dy = aura.direction
        x = aura.rect.centerx
        y = aura.rect.centery

        if not aura.frozen:
            x += dx * speed
            y += dy * speed

        x = max(bounds["left"], min(bounds["right"], x))
        y = max(bounds["top"], min(bounds["bottom"], y))

        if x in (bounds["left"], bounds["right"]) and y in (bounds["top"], bounds["bottom"]):
            aura.frozen = True
            aura.frozen_wait_time = random.randint(20,60)
            aura.speed = 10
            if dx != 0: 
                usual_turn = (0, 1 if y == bounds["top"] else -1)
                reverse = (-dx, 0)
            else:
                usual_turn = (1 if x == bounds["left"] else -1, 0)
                reverse = (0, -dy)

            aura.direction = usual_turn if random.random() > 1/5 else reverse
            aura.bullet_color_index = 6 if aura.bullet_color_index == 4 else 4

        aura.rect.center = (x, y)

    def create_beam(self, cycle_frame, angle=90, color_index=2):
        if cycle_frame != 0 or not self.shooting_beams:
            return
        start_x, start_y = self.rect.center
        Boss_Bullet(start_x, start_y, self.beam_sprites["Projectiles_beam"][color_index], self.window, 0, angle, 255, 2, "beam", 0, self.beams)
        beam = self.beams.sprites()[-1]
        beam.start_pos = self.rect.center
        beam.width = 16*beam.scale
        self.update_beam(beam)


    def update_beam(self, beam, length = 300, screen_length=True):
        start_x, start_y = beam.start_pos
        angle = math.radians(beam.angle_direction)
        dx, dy = math.cos(angle), math.sin(angle)

        if screen_length:
            screen_width, screen_height = 600, 750
            edge_distances = []

            if dx > 0:
                edge_distances.append((screen_width - start_x) / dx)
            elif dx < 0:
                edge_distances.append(-start_x / dx)

            if dy > 0:
                edge_distances.append((screen_height - start_y) / dy)
            elif dy < 0:
                edge_distances.append(-start_y / dy)

        length = max(1, round(min(distance for distance in edge_distances if distance >= 0))) if screen_length else length
        thickness = max(1, round(beam.width))

        vertical_image = pygame.transform.smoothscale(beam.original_image, (thickness, length))

        end_mask = pygame.Surface((thickness, length), pygame.SRCALPHA)
        pygame.draw.rect(
            end_mask,
            (255, 255, 255, 255),
            end_mask.get_rect(),
            border_radius=thickness // 2,
        )
        vertical_image.blit(end_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        beam.image = pygame.transform.rotate(vertical_image, 90 - beam.angle_direction)

        end_x = start_x + dx * length
        end_y = start_y + dy * length
        beam.rect = beam.image.get_rect(center=(round((start_x + end_x) / 2), round((start_y + end_y) / 2)))
        beam.mask = pygame.mask.from_surface(beam.image)

    def beam_sweep(self, start_angle, end_angle, speed=2.25):
        if not self.beam_angle_start_set:
            self.beam_angle_start_set = True
            self.beam_angle = start_angle % 360
            return

        self.beam_angle = (self.beam_angle + speed * self.beam_direction) % 360

        if self.angle_distance(self.beam_angle, end_angle) <= speed:
            self.beam_angle = end_angle % 360
            self.beam_direction *= -1
            self.beam_angle_start_set = False
            if self.first_sweep:
                self.shooting_beams = True

    def angle_distance(self, current, target):
        delta = (target - current) % 360
        if delta > 180:
            delta -= 360
        return abs(delta)

    def draw(self):
        self.particles.draw(self.window)
        self.leftovers.draw(self.window)
        self.cranberry_auras.draw(self.window)
        self.beams.draw(self.window)
        self.fogs.draw(self.window)
        self.window.blit(self.image, self.rect)
        self.bullets.draw(self.window)
