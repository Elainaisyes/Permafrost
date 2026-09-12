import pygame
from os import listdir
from os.path import isfile, join

def flip (sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(image_name, sprite_width=24, sprite_height=31, expected_cols=8, direction="right"):
    path = f"assets/images/{image_name}"
    images = [f for f in listdir(path) if isfile(join(path, f))]
    all_sprites = {}

    for image in images:
        sheet = pygame.image.load(join(path, image)).convert_alpha()

        cols = expected_cols
        rows = sheet.get_height() // sprite_height

        for row in range(rows):
            sprites = []
            for col in range(cols):
                rect = pygame.Rect(
                    col * sprite_width,
                    row * sprite_height,
                    sprite_width,
                    sprite_height
                )
                sprite = sheet.subsurface(rect).copy()
                sprite = pygame.transform.scale(sprite, (sprite_width * 2.5, sprite_height * 2.5))
                sprites.append(sprite)

            key = image.replace(".png", "")
            if direction:
                all_sprites[f"{key}_row{row}_right"] = sprites
                all_sprites[f"{key}_row{row}_left"] = flip(sprites)
            else:
                all_sprites[f"{key}_row{row}"] = sprites

    return all_sprites