import pygame

def scale_mask(image, scale):
    full_mask = pygame.mask.from_surface(image)
    width, height = full_mask.get_size()

    small_size = (max(1, round(width * scale)), max(1, round(height * scale)))
    small_mask = full_mask.scale(small_size)

    mask = pygame.Mask((width, height))
    offset = (
        (width - small_size[0]) // 2,
        (height - small_size[1]) // 2,
    )
    mask.draw(small_mask, offset)
    return mask