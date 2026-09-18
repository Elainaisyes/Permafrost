import pygame
from classes.player import Player
from classes.background import Background
from util.return_letters import return_letters
from util.set_text import set_text

# Default buffer is often 2048; reducing to 512 eliminates lag
pygame.mixer.pre_init(44100, -16, 2, 512)

pygame.init()

pygame.mixer.init()
pygame.mixer.set_num_channels(64)

pygame.mixer.music.load("assets/audios/U.N. Owen Was Her.mp3")
pygame.mixer.music.play(loops=-1, start=2.0, fade_ms=5000)
pygame.mixer.music.set_volume(0.75)

BG_COLOR = (0, 0, 0)
WIDTH, HEIGHT = 1000, 750
SIDEBAR_WIDTH = WIDTH * 0.4
GAME_WIDTH = WIDTH-SIDEBAR_WIDTH
GAME_NAME = "Permafrost"
FPS = 60

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(GAME_NAME)

programIcon = pygame.image.load('assets/images/Program_Icon/Fumo.png')
pygame.display.set_icon(programIcon)

letters = pygame.sprite.Group()
LETTERS_DICT = return_letters()
LETTER_SIZE = 16
DEFAULT_TEXT_SETUP = (LETTERS_DICT, LETTER_SIZE, window, letters)

main_background = Background(0, 0, WIDTH-SIDEBAR_WIDTH, HEIGHT, 'Game_Background.png', window)
sidebar = Background(WIDTH-SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT, 'Sidebar_Background.png', window)

set_text("FLANDRE SCARLET", 20, 20, *DEFAULT_TEXT_SETUP, 1.5, 1, (255,255,35,255))
set_text("9", 190, 18, *DEFAULT_TEXT_SETUP, 1, 1.5, (255,255,100,255))

set_text("HiScore", GAME_WIDTH + 20, 100, *DEFAULT_TEXT_SETUP, 1.125, 1)
set_text("012673632", GAME_WIDTH + 20 + 130, 98, *DEFAULT_TEXT_SETUP, 0.6, 1.25)
set_text("Score", GAME_WIDTH + 20, 140, *DEFAULT_TEXT_SETUP, 1.125, 1)
set_text("927397625", GAME_WIDTH + 20 + 130, 138, *DEFAULT_TEXT_SETUP, 0.6, 1.25)

set_text("Player", GAME_WIDTH + 20, 220, *DEFAULT_TEXT_SETUP, 1.125, 1)
set_text("Bomb", GAME_WIDTH + 20, 260, *DEFAULT_TEXT_SETUP, 1.125, 1)

set_text("Power", GAME_WIDTH + 20, 340, *DEFAULT_TEXT_SETUP, 1.125, 1)
set_text("Graze", GAME_WIDTH + 20, 380, *DEFAULT_TEXT_SETUP, 1.125, 1)

def draw (window, player):
    main_background.draw()
    sidebar.draw()
    player.draw()
    letters.draw(window)
    pygame.display.update()

def main(window):
    running = True
    clock = pygame.time.Clock()
    player = Player(GAME_WIDTH // 2 - 32, HEIGHT // 2, window, GAME_WIDTH)
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