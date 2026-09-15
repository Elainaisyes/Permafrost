import pygame
from os import listdir
from os.path import isfile, join
from classes.player import Player

pygame.init()

BG_COLOR = (0, 0, 0)
WIDTH, HEIGHT = 1000, 750
GAME_NAME = "Permafrost"
FPS = 60

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(GAME_NAME)

programIcon = pygame.image.load('assets/images/Program_Icon/Fumo.png')
pygame.display.set_icon(programIcon)

def draw (window, player):
    player.draw()
    pygame.display.update()

def main(window):
    running = True
    clock = pygame.time.Clock()
    player = Player(WIDTH // 2, HEIGHT // 2, window)
    while running: 
        clock.tick(FPS)
        window.fill(BG_COLOR)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.loop()
        draw(window, player)


    pygame.quit()



if __name__ == "__main__":
    main(window)