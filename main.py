import pygame
from classes.player import Player
from classes.boss import Boss
from classes.background import Background
from classes.basic_image import Basic_Image
from classes.bar import Bar
from util.return_letters import return_letters
from util.set_text import set_text

# eliminates lag
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

SIDEBAR_OFFSET_PLACEMENT = GAME_WIDTH + 120

stars = pygame.sprite.Group()
red_star = pygame.image.load("assets/images/Star/Red_Star.png").convert_alpha()
green_star = pygame.image.load("assets/images/Star/Green_Star.png").convert_alpha()

main_background = Background(0, 0, WIDTH-SIDEBAR_WIDTH, HEIGHT, 'Game_Background.png', window)
sidebar = Background(WIDTH-SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT, 'Sidebar_Background.png', window)

bars = pygame.sprite.Group()
power_bar_container = Bar(SIDEBAR_OFFSET_PLACEMENT, 330, 235, 30, (60, 60, 60), window, bars, has_border=True, border_color=(255,255,255))
power_bar = Bar(SIDEBAR_OFFSET_PLACEMENT + 7.5, 337.5, 220, 17.5, (150, 150, 150), window, bars, border_radius=0, is_gradient=True,
                gradient_start_color=(255,255,255), gradient_end_color=(90,140,255))

def update_stars(player):
    stars.empty()

    for i in range(player.health):
        Basic_Image(red_star, SIDEBAR_OFFSET_PLACEMENT + 26 * i, 215, 16, 16, 1.5, window, stars)

    for i in range(player.bombs):
        Basic_Image(green_star, SIDEBAR_OFFSET_PLACEMENT + 26 * i, 255, 16, 16, 1.5, window, stars)

def draw (window, player, boss):
    main_background.draw()
    boss.aura.draw()
    player.draw()
    boss.draw()
    sidebar.draw()
    stars.draw(window)
    letters.draw(window)
    bars.draw(window)
    pygame.display.update()

def main(window):
    running = True
    clock = pygame.time.Clock()
    player = Player(GAME_WIDTH // 2 - 32, HEIGHT // 2, window, GAME_WIDTH)
    boss = Boss(GAME_WIDTH // 2 - 38, 50, window, GAME_WIDTH)

    set_text("FLANDRE SCARLET", 20, 20, *DEFAULT_TEXT_SETUP, 1.5, 1, (255,255,35,255))
    set_text("9", 200, 18, *DEFAULT_TEXT_SETUP, 1, 1.5, (255,255,100,255))

    set_text("HiScore", GAME_WIDTH + 20, 100, *DEFAULT_TEXT_SETUP, 1.5, 1)
    set_text(f"{(9 - len(str(player.highscore))) * "0" + str(player.highscore)}", SIDEBAR_OFFSET_PLACEMENT, 98, *DEFAULT_TEXT_SETUP, 0.675, 1.25)
    set_text("Score", GAME_WIDTH + 20, 140, *DEFAULT_TEXT_SETUP, 1.5, 1)
    set_text(f"{(9 - len(str(player.score))) * "0" + str(player.score)}", SIDEBAR_OFFSET_PLACEMENT, 138, *DEFAULT_TEXT_SETUP, 0.675, 1.25)

    set_text("Player", GAME_WIDTH + 20, 220, *DEFAULT_TEXT_SETUP, 1.5, 1, (255, 88, 88))
    set_text("Bomb", GAME_WIDTH + 20, 260, *DEFAULT_TEXT_SETUP, 1.5, 1, (67, 177, 86))

    set_text("Power", GAME_WIDTH + 20, 340, *DEFAULT_TEXT_SETUP, 1.5, 1, (255, 138, 138))
    set_text("Graze", GAME_WIDTH + 20, 380, *DEFAULT_TEXT_SETUP, 1.5, 1, (127, 237, 146))
    set_text(f"{player.graze}", SIDEBAR_OFFSET_PLACEMENT, 378, *DEFAULT_TEXT_SETUP, 0.75, 1.25)

    # Optimization helpers, ensures no needless running
    last_health = None
    last_bombs = None
    while running: 
        clock.tick(FPS)
        window.fill(BG_COLOR)
        if player.health != last_health or player.bombs != last_bombs:
            update_stars(player)
            last_health = player.health
            last_bombs = player.bombs

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                boss.desired_x, boss.desired_y = pygame.mouse.get_pos()

        player.loop()
        boss.loop(player)
        draw(window, player, boss)


    pygame.quit()



if __name__ == "__main__":
    main(window)