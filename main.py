import pygame
from os import listdir
from os.path import isfile, join
from classes.player import Player
from classes.background import Background
from classes.letter import Letter
from util.load_sprite_sheets import load_sprite_sheets
from util.return_letters import return_letters
from util.set_text import set_text

pygame.init()

BG_COLOR = (0, 0, 0)
WIDTH, HEIGHT = 1000, 750
SIDEBAR_WIDTH = WIDTH * 0.4
GAME_WIDTH = WIDTH-SIDEBAR_WIDTH
GAME_NAME = "Permafrost"
FPS = 60
LETTER_SIZE = 16

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(GAME_NAME)

programIcon = pygame.image.load('assets/images/Program_Icon/Fumo.png')
pygame.display.set_icon(programIcon)

LETTERS_DICT = return_letters()
letters = pygame.sprite.Group()
DEFAULT_TEXT_FORMAT = (LETTERS_DICT, LETTER_SIZE, 1.125, window, letters)

main_background = Background(0, 0, WIDTH-SIDEBAR_WIDTH, HEIGHT, 'Game_Background.png', window)
sidebar = Background(WIDTH-SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT, 'Sidebar_Background.png', window)
set_text("Flandre Scarlet", 200, 200, *DEFAULT_TEXT_FORMAT)
def draw (window, player):
    main_background.draw()
    sidebar.draw()
    player.draw()
    letters.draw(window)
    pygame.display.update()

def main(window):
    running = True
    clock = pygame.time.Clock()
    player = Player(GAME_WIDTH // 2-32, HEIGHT // 2, window, GAME_WIDTH)
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