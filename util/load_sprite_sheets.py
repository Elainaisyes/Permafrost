import pygame, os
from os import listdir
from os.path import isfile, join

def flip (sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(image_name, sprite_width, sprite_height, expected_cols, scale_factor = 1, direction=None):
    path = f"assets/images/{image_name}"
    images = [f for f in listdir(path) if isfile(join(path, f))]
    all_sprites = {}

    for image in images:
        sheet = pygame.image.load(join(path, image)).convert_alpha()

        cols = min(expected_cols, sheet.get_width() // sprite_width)
        rows = min(sheet.get_height() // sprite_height, 999)

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
                sprite = pygame.transform.scale(sprite, (sprite_width * scale_factor, sprite_height * scale_factor))
                sprites.append(sprite)

            key = image.replace(".png", "")
            if direction:
                all_sprites[f"{key}_row{row}_right"] = sprites
                all_sprites[f"{key}_row{row}_left"] = flip(sprites)
            else:
                all_sprites[f"{key}_row{row}"] = sprites

    return all_sprites
        

def load_sprite_sheet_row(image_name, sprite_width, sprite_height, expected_cols, row_start, x_offset, scale_factor=1, name="bullet", direction = None):    
    path = f"assets/images/{image_name}"
    images = [f for f in listdir(path) if isfile(join(path, f))]
    all_sprites = {}

    for image in images:
        sheet = pygame.image.load(join(path, image)).convert_alpha()

        if row_start < 0 or row_start + sprite_height > sheet.get_height():
            continue

        cols = min(expected_cols, (sheet.get_width() - x_offset) // sprite_width)
        if cols <= 0:
            continue

        sprites = []

        for col in range(cols):
            x = x_offset + col * sprite_width
            y = row_start

            if x + sprite_width > sheet.get_width():
                break

            rect = pygame.Rect(x, y, sprite_width, sprite_height)
            sprite = sheet.subsurface(rect).copy()
            sprite = pygame.transform.scale(sprite, (sprite_width * scale_factor, sprite_height * scale_factor))
            sprites.append(sprite)

        key = image.replace(".png", "")
        if direction:
            all_sprites[f"{key}_{name}_right"] = sprites
            all_sprites[f"{key}_{name}_left"] = flip(sprites)
        else:
            all_sprites[f"{key}_{name}"] = sprites
    return all_sprites