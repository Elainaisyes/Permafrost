import pygame
from os import listdir
from os.path import isfile, join
from classes.player import Player
from classes.background import Background
from load_sprite_sheets import load_sprite_sheets

pygame.init()

BG_COLOR = (0, 0, 0)
WIDTH, HEIGHT = 1000, 750
SIDEBAR_WIDTH = WIDTH * 0.4
GAME_NAME = "Permafrost"
FPS = 60

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(GAME_NAME)

programIcon = pygame.image.load('assets/images/Program_Icon/Fumo.png')
pygame.display.set_icon(programIcon)

main_background = Background(0, 0, WIDTH-SIDEBAR_WIDTH, HEIGHT, 'Game_Background.png', window)
sidebar = Background(WIDTH-SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT, 'Sidebar_Background.png', window)

def draw (window, player):
    main_background.draw()
    sidebar.draw()
    player.draw()
    pygame.display.update()

def main(window):
    running = True
    clock = pygame.time.Clock()
    player = Player(WIDTH // 2, HEIGHT // 2, window, WIDTH-SIDEBAR_WIDTH)
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