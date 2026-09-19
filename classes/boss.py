import pygame, math
from util.load_sprite_sheets import load_sprite_sheets

class Boss(pygame.sprite.Sprite):
    ANIMATION_DELAY = 4
    MAX_SPEED = 6
    SHOOT_DELAY = 4

    # Sprite rows
    IDLE_FORWARDS = "Flandre_row0_"
    IDLE_FORWARDS_TURNED = "Flandre_row1_"
    IDLE_BACKWARDS = "Flandre_row4_"
    IDLE_BACKWARDS_TURNED = "Flandre_row3_"
    MOVING = "Flandre_row2_"
    FLY_UP = "Flandre_row1_"
    FLY_DOWN = "Flandre_row3_"

    def __init__(self, x, y, window, player, screen_width = 600):
        super().__init__()
        self.sprites = load_sprite_sheets("Flandre", 24, 32, 8, 2.5, "right")
        self.image = self.sprites[f"{self.IDLE_BACKWARDS}right"][0]
        self.x_pos = float(x)
        self.y_pos = float(y)
        self.rect = self.image.get_rect(topleft=(self.x_pos, self.y_pos))
        self.x_velocity, self.y_velocity = self.MAX_SPEED, self.MAX_SPEED
        self.animation_count = 0
        self.angle_direction = 270
        self.direction = "right"
        self.speed = self.MAX_SPEED
        self.desired_x, self.desired_y = 20,20

        self.window = window

    def move(self, dx, dy, player):
        target_x = player.x_pos - self.rect.centerx
        target_y = player.y_pos - self.rect.centery
        distance = math.hypot(target_x, target_y)

        print(self.angle_direction)
        if distance <= self.speed:
            self.rect.center = (self.desired_x, self.desired_y)
            self.x_pos, self.y_pos = self.rect.topleft
            self.x_velocity = self.y_velocity = 0
            self.angle_direction = -90
            return

        self.angle_direction = math.degrees(math.atan2(-target_y, target_x))

        self.x_pos += target_x / distance * self.speed
        self.y_pos += target_y / distance * self.speed
        self.rect.topleft = (round(self.x_pos), round(self.y_pos))

    def loop(self, player):
        self.move(self.x_velocity, self.y_velocity, player)
        self.update_sprites()

    def update_sprites(self):
        sprites = self.sprites[f"{self.IDLE_BACKWARDS}{self.direction}"]

        angle = self.angle_direction % 360
        sector = int((angle + 22.5) // 45) % 8
        # add thediagnokl angles later, need to increase sector size
        if sector == 0:
            sprites = self.sprites[f"{self.MOVING}right"]
        elif sector == 1:
            sprites = self.sprites[f"{self.FLY_UP}right"]
        elif sector == 2:
            sprites = self.sprites[f"{self.IDLE_FORWARDS}right"]
        elif sector == 3:
            sprites = self.sprites[f"{self.FLY_UP}left"]
        elif sector == 4:
            sprites = self.sprites[f"{self.MOVING}left"]
        elif sector == 5:
            sprites = self.sprites[f"{self.FLY_DOWN}left"]
        elif sector == 6:
            sprites = self.sprites[f"{self.IDLE_BACKWARDS}right"]
        elif sector == 7:
            sprites = self.sprites[f"{self.FLY_DOWN}right"]
            
            
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites) // 2
        self.animation_count += 1
        self.image = sprites[sprite_index]

        if sector % 2 == 1:
            self.image = sprites[4]

    def draw(self):
        self.window.blit(self.image, self.rect)