import pygame, random
from classes.player import Player
from classes.boss import Boss
from classes.basic_image import Basic_Image
from classes.bar import Bar
from classes.particle import Particle
from util.return_letters import return_letters
from util.set_text import set_text, get_line_breaks, get_line_width
from util.audio_manager import play_sound, play_bgm, pause_bgm, resume_bgm

# eliminates lag
pygame.mixer.pre_init(44100, -16, 2, 512)

pygame.init()

pygame.mixer.init()
pygame.mixer.set_num_channels(128)

BG_COLOR = (0, 0, 0)
WIDTH, HEIGHT = 1000, 750
GAME_ASPECT = WIDTH / HEIGHT
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
DEFAULT_TEXT_SETUP = (LETTERS_DICT, LETTER_SIZE, window)

highscore_text = pygame.sprite.Group()
score_text = pygame.sprite.Group()
power_text = pygame.sprite.Group()
graze_text = pygame.sprite.Group()
attacks_left_text = pygame.sprite.Group()
phase_timer_text = pygame.sprite.Group()
spellcard_text = pygame.sprite.Group()

title_text = pygame.sprite.Group()
menu_options_text = pygame.sprite.Group()
pause_options_text = pygame.sprite.Group()

SIDEBAR_OFFSET_PLACEMENT = GAME_WIDTH + 120

paused = False
screen = "game"

stars = pygame.sprite.Group()
red_star = pygame.image.load("assets/images/Star/Red_Star.png").convert_alpha()
green_star = pygame.image.load("assets/images/Star/Green_Star.png").convert_alpha()

main_background = Basic_Image(pygame.image.load("assets/images/Window_Background/Game_Background.png").convert_alpha(), 0, 0, WIDTH-SIDEBAR_WIDTH+50, HEIGHT, 1, window)
spellcard_background = Basic_Image(pygame.image.load("assets/images/Window_Background/Spellcard_Background.png").convert_alpha(), 0, 0, WIDTH-SIDEBAR_WIDTH, HEIGHT, 1, window, alpha=0)
sidebar = Basic_Image(pygame.image.load("assets/images/Window_Background/Sidebar_Background.png").convert_alpha(), WIDTH-SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT, 1, window)

menu_background = Basic_Image(pygame.image.load("assets/images/Window_Background/Menu_Background.jpeg").convert_alpha(), 0, 0, WIDTH, HEIGHT, 1, window)
cirno_portrait = Basic_Image(pygame.image.load("assets/images/Other/Cirno_Portrait/Normal.png").convert_alpha(), (WIDTH-SIDEBAR_WIDTH)//2-400, HEIGHT//2-100, 500, 500, 1, window)
cirno_portrait_particles = pygame.sprite.Group()


frost_aura = Basic_Image(pygame.image.load("assets/images/Aura/Aura.png").convert_alpha(), (WIDTH-SIDEBAR_WIDTH)//2-400, HEIGHT//2-100, 500, 500, 1, window, color=(200, 200, 255))
frost_aura.image_base = frost_aura.image.copy()

blackout_overlay = Basic_Image(pygame.image.load("assets/images/Window_Background/Sidebar_Background.png").convert_alpha(), 0, 0, WIDTH, HEIGHT, 1, window, color=(0,0,200))
blackout_overlay.alpha_direction = 1
blackout_overlay.alpha_changing = True
blackout_overlay.will_change_screen = False

pause_darken_overlay = Basic_Image(pygame.image.load("assets/images/Window_Background/Sidebar_Background.png").convert_alpha(), 0, 0, WIDTH, HEIGHT, 1, window, color=(0,0,0, 255), alpha=0)

player = Player(GAME_WIDTH // 2 - 32, HEIGHT // 2, window, GAME_WIDTH)
boss = Boss(GAME_WIDTH // 2 - 38, 50, window, player, GAME_WIDTH)

bars = pygame.sprite.Group()

boss_health_bar = Bar(220, 27, 300, 5, (255, 255, 255), window, bars, is_gradient=True, 
                gradient_start_color=(255,255,35), gradient_end_color=(255,100,100), max_height=5, vertical=True)

spellcard_bar = Bar(220, 37, 290, LETTER_SIZE, (255, 255, 255), window, is_gradient=True, border_radius=200,
                gradient_start_color=(83, 70, 199, 0), gradient_end_color=(83, 70, 199, 150), max_height=LETTER_SIZE, vertical=True)

boss_spellcard_image = Basic_Image(pygame.image.load("assets/images/Other/Flandre_Spellcard.png").convert_alpha(), 470, 350, 500, 500, 0.7, window)

power_bar_container = Bar(SIDEBAR_OFFSET_PLACEMENT, 330, 235, 30, (30, 30, 30), window, bars, has_border=True, border_color=(255,255,255))
power_bar = Bar(SIDEBAR_OFFSET_PLACEMENT + 5, 335, 225, 20, (255, 255, 255), window, bars, is_gradient=True,
                gradient_start_color=(255,255,255), gradient_end_color=(90,140,255), max_width=225)

set_text("TOUHOU EIKYUUTOUDO", 20, 20, *DEFAULT_TEXT_SETUP, title_text, 1.2, 2.5, (200,200,255,255), text_shadow=(3, 3, (220,220,255, 120)))
set_text("PERMAFROST", 20, 100, *DEFAULT_TEXT_SETUP, title_text, 1.35, 2.5, (200,200,255,255), text_shadow=(3, 3, (220,220,255, 120)))

set_text("FLANDRE SCARLET", 20, 20, *DEFAULT_TEXT_SETUP, letters, 1.5, 1, (255,255,35,255))
set_text(str(boss.attacks_left), 200, 18, *DEFAULT_TEXT_SETUP, attacks_left_text, 1, 1.5, (255,255,100,255))
set_text(str(boss.phase_timer), GAME_WIDTH - 50, 18, *DEFAULT_TEXT_SETUP, phase_timer_text, 1, 1.5, (190,220,255,255))

set_text("LUNATIC", GAME_WIDTH + 16*1.75*7/3, 35, *DEFAULT_TEXT_SETUP, letters, 0.7, 1.75, (205, 20, 185))
set_text("HiScore", GAME_WIDTH + 20, 100, *DEFAULT_TEXT_SETUP, letters, 1.5, 1, (255, 255, 225))
set_text(str(player.highscore).zfill(9), SIDEBAR_OFFSET_PLACEMENT, 98, *DEFAULT_TEXT_SETUP, highscore_text,  0.675, 1.25, (255, 255, 225))
set_text("Score", GAME_WIDTH + 20, 140, *DEFAULT_TEXT_SETUP, letters,  1.5, 1)
set_text(str(player.score).zfill(9), SIDEBAR_OFFSET_PLACEMENT, 138, *DEFAULT_TEXT_SETUP, score_text,  0.675, 1.25)

set_text("Player", GAME_WIDTH + 20, 220, *DEFAULT_TEXT_SETUP, letters,  1.5, 1, (255, 88, 88))
set_text("Bomb", GAME_WIDTH + 20, 260, *DEFAULT_TEXT_SETUP, letters,  1.5, 1, (67, 177, 86))

set_text("Power", GAME_WIDTH + 20, 335, *DEFAULT_TEXT_SETUP, letters,  1.5, 1, (149, 223, 255))
set_text(str(int(player.power)), power_bar_container.x_pos + power_bar_container.width/2 - 12, 335, *DEFAULT_TEXT_SETUP, power_text,  1.5, 1.5, (195, 232, 255))
set_text("Graze", GAME_WIDTH + 20, 380, *DEFAULT_TEXT_SETUP, letters,  1.5, 1, (127, 237, 146))
set_text(str(player.graze), SIDEBAR_OFFSET_PLACEMENT, 378, *DEFAULT_TEXT_SETUP, graze_text,  0.75, 1.25, (127, 237, 146))

def lerp(start, end, multiplier):
    return start + (end - start) * multiplier

def basic_text_update(tracker, tracked, group, *args):
    if tracked != tracker:
        group.empty()
        tracker = tracked
        set_text(*args)
        return tracker
    return tracker

def update_stars(player):
    stars.empty()

    for i in range(player.health):
        Basic_Image(red_star, SIDEBAR_OFFSET_PLACEMENT + 26 * i, 215, 16, 16, 1.5, window, stars)

    for i in range(player.bombs):
        Basic_Image(green_star, SIDEBAR_OFFSET_PLACEMENT + 26 * i, 255, 16, 16, 1.5, window, stars)    

def update_bars(player, container, bar) :
    if player.power >= 125:
        container.is_gradient = True
        container.gradient_start_color = (13, 113, 170)
        container.gradient_end_color = (73, 153, 210)
        bar.gradient_end_color = (195, 232, 255)
        container.build_image()
        bar.build_image()
    else:
        container.is_gradient = container.default_is_gradient
        container.gradient_start_color = container.default_gradient_start_color
        container.gradient_end_color = container.default_gradient_end_color
        bar.gradient_end_color = bar.default_gradient_end_color
        container.build_image()
        bar.build_image()

def update_spellcard_bar(spellcard_bar, boss, last_text_group, tracker):
    text = str(boss.phase.name) if boss.phase.name is not None else boss.phases[boss.phase_index-1].name
    last_text_group = basic_text_update(last_text_group, tracker, spellcard_text, 
                    text, spellcard_bar.x_pos + 10, spellcard_bar.y_pos+5, *DEFAULT_TEXT_SETUP, spellcard_text,  1.4, 0.9, (190,220,255), 280)
    line_breaks = get_line_breaks() + 1 
    line_width = get_line_width()
    height = LETTER_SIZE * line_breaks + 5
    spellcard_bar.height, spellcard_bar.max_height = height, height
    spellcard_bar.width = int(line_width) + 20
    spellcard_bar.build_image()
    return last_text_group

def set_spellcard_image(scale_factor, alpha):
    boss_spellcard_image.scale_factor = scale_factor
    boss_spellcard_image.image = pygame.transform.smoothscale(boss_spellcard_image.original_image.copy(), (int(500 * boss_spellcard_image.scale_factor), int(500 * boss_spellcard_image.scale_factor)))
    boss_spellcard_image.alpha = alpha
    boss_spellcard_image.image.set_alpha(int(boss_spellcard_image.alpha))
    boss_spellcard_image.rect = boss_spellcard_image.image.get_rect(center=boss_spellcard_image.rect.center)

def update_cirno_portrait(option):
    portrait = pygame.image.load(f"assets/images/Other/Cirno_Portrait/{option['Cirno_Portrait']}.png").convert_alpha()
    portrait_center = cirno_portrait.rect.center
    cirno_portrait.image = pygame.transform.smoothscale(portrait, cirno_portrait.rect.size)
    cirno_portrait.rect = cirno_portrait.image.get_rect(center=portrait_center)

def build_menu_options(specs, start_x, start_y, group, starting_label, x_factor_multiplier=40, primary_color=(220,220,255), secondary_color=(200,200,255, 180)):
    options = {}
    keys = []
    colors = {"primary": primary_color, "secondary": secondary_color}

    for label, y_offset, x_factor, portrait, spacing, scale in specs:
        x = start_x + x_factor * x_factor_multiplier
        y = start_y + y_offset
        color = primary_color if label == starting_label else secondary_color
        text_shadow=(2, 2, (*primary_color, 120 if label == "Start" else 50))

        set_text(label, x, y, *DEFAULT_TEXT_SETUP, group, spacing, scale, color=color, text_shadow=text_shadow)
        options[label] = {
            "x": x,
            "y": y,
            "width": get_line_width(),
            "Cirno_Portrait": portrait
        }
        keys.append(label)

    return options, keys, colors

menu_specs = [
    ("Start", 0, -1, "Normal", 1.35, 1.85),
    ("Spell Practice", 80, -2/3, "Confident", 1.35, 1.75),
    ("Score", 160, -1/3, "Startled", 1.35, 1.75),
    ("Music Room", 240, 0, "Happy", 1.35, 1.75),
    ("Options", 320, -1/3, "Sigh", 1.35, 1.75),
    ("Credits", 400, -2/3, "Sigh", 1.35, 1.75),
    ("Quit", 480, -1, "Shock", 1.35, 1.75),
]

menu_options, menu_options_keys, menu_option_colors = build_menu_options(menu_specs, 650, 150, menu_options_text, "Start")

pause_specs = [
    ("Continue", 0, 0, "Normal", 1.35, 1.85),
    ("Restart", 80, 0, "Normal", 1.35, 1.85),
    ("Options", 160, 0, "Normal", 1.35, 1.85),
    ("Back to Menu", 240, 0, "Normal", 1.35, 1.85),
]

pause_options, pause_options_keys, pause_option_colors = build_menu_options(pause_specs, 220, 220, pause_options_text, "Continue", primary_color=(255,125,125), secondary_color=(255,105,105,180))
for letter in pause_options_text:
    letter.alpha = 0
    letter.image.set_alpha(0)

option_bar = Bar(menu_options["Start"]["x"]-5, menu_options["Start"]["y"]+35, round(menu_options["Start"]["width"]+20), 7, (255,255,255), window, is_gradient=True, gradient_start_color=(200,200,255,255), gradient_end_color=(220,220,255,255), border_radius=100)
menu_options_keys = [option for option in menu_options.keys()]
option_bar.particles = pygame.sprite.Group()
option_bar.alpha = 255

menu_option_index = 0
menu_option = menu_options_keys[menu_option_index]

pause_option_index = 0
pause_option = pause_options_keys[pause_option_index]

option_indicator = Basic_Image(player.bullet_sprites["Projectiles_bullet"][7], menu_options[menu_option]["x"]-30, menu_options[menu_option]["y"]+6, 16, 16, 1.75, window, rotation_angle=90)

def set_option(index, options, options_keys, group, colors, state_name):
    global menu_option, menu_option_index, pause_option, pause_option_index

    selected_index = max(0, min(index, len(options_keys) - 1))
    selected_option = options_keys[selected_index]

    active_option = "NOT EMPTY"

    if state_name == "menu":
        menu_option_index = selected_index
        menu_option = selected_option
    elif paused:
        pause_option_index = selected_index
        pause_option = selected_option
        
    option_bar.y_pos = options[selected_option]["y"] + 35
    option_bar.x_pos = options[selected_option]["x"] - 5
    option_bar.width = options[selected_option]["width"] + 20
    option_bar.max_width = round(options[selected_option]["width"] + 20)
    option_bar.gradient_start_color = colors["secondary"]
    option_bar.gradient_end_color = (*colors["secondary"][:3], 255)
    option_bar.build_image()

    group.empty()
    for i, option in enumerate(options_keys):
        selected = i == selected_index
        position = options[option]
        color = colors["primary"] if selected else colors["secondary"]
        shadow_alpha = 120 if selected else 50
        scale = 1.85 if selected else 1.75

        set_text(
            option, position["x"], position["y"], *DEFAULT_TEXT_SETUP,
            group, 1.35, scale, color,
            text_shadow=(2, 2, (*colors["primary"], shadow_alpha))
        )

        if selected:
            option_indicator.rect.center = (
                position["x"] - 30 + option_bar.offset * 3,
                position["y"] + 18
            )

    update_cirno_portrait(options[selected_option])
    play_sound(pygame.mixer.Sound("assets/audios/sfx/blip.mp3"), 0.25)
    return selected_index

def change_screen_setup():
    blackout_overlay.alpha_changing = True
    player.invulnerable = True
    player.invulnerability_frames = 60
    pause_bgm()
    blackout_overlay.will_change_screen = True

    if screen == "menu" or screen == "game":
        boss.pause_time = 30
    if screen == "menu":
        update_cirno_portrait(menu_options["Music Room"])
    else:
        update_cirno_portrait(menu_options[menu_option])

def set_mouse_rects(event, options, options_keys):
    mouse_x, mouse_y = event.pos
    largest_width = 0
    for option in options_keys:
        if options[option]["width"] > largest_width:
            largest_width = options[option]["width"]
            
    for index, option in enumerate(options_keys):
        pos = options[option]
        rect = pygame.Rect(pos["x"] - 40, pos["y"] - 10, largest_width + 80, 60)
        if rect.collidepoint(mouse_x, mouse_y):
            return index
    return None

def mouse_selection_change(event, options, options_keys, index, group, colors, state_name):
    selected_index = set_mouse_rects(event, options, options_keys)
    if selected_index is not None and selected_index != index:
        return set_option(selected_index, options, options_keys, group, colors, state_name)

def draw (window, player, boss):
    if screen == "game":
        main_background.draw()
        spellcard_background.draw()
        boss.aura.draw()
        player.draw()
        boss.draw()
        if boss.phase_index > 0:
            boss_spellcard_image.draw()
            spellcard_bar.draw()
            spellcard_text.draw(window)
        sidebar.draw()
        bars.draw(window)
        stars.draw(window)
        letters.draw(window)
        attacks_left_text.draw(window)
        phase_timer_text.draw(window)
        highscore_text.draw(window) 
        score_text.draw(window)
        power_text.draw(window)
        graze_text.draw(window)
        pause_darken_overlay.draw()
        pause_options_text.draw(window)
    elif screen == "menu":
        menu_background.draw()
        frost_aura.draw()
        cirno_portrait_particles.draw(window)
        cirno_portrait.draw()
        title_text.draw(window)
        menu_options_text.draw(window)

    if screen == "game" or screen == "menu" or screen == "gameover":
        option_bar.particles.draw(window)
        option_bar.draw()
        option_indicator.draw()

    blackout_overlay.draw()
    pygame.display.update()

def main(window):
    running = True
    fullscreen = False
    global paused, screen, menu_option_index, pause_option_index

    play_bgm(screen)
    title_color_offset = 0
    title_color_offset_direction = 1

    screen_change_ready = False

    active_options = "menu"

    clock = pygame.time.Clock()

    # Optimization helpers, ensures no needless running
    last_attacks_left = None
    last_phase_timer = None
    last_boss_health = None
    last_highscore = None
    last_score = None
    last_health = None
    last_bombs = None
    last_power = None
    last_graze = None
    last_spellcard_text = None

    last_title_color_offset = None
    last_frost_aura_rotation = None

    while running: 
        clock.tick(FPS)
        window.fill(BG_COLOR)

        last_attacks_left = basic_text_update(last_attacks_left, boss.attacks_left, attacks_left_text, 
                          str(boss.attacks_left), 190, 16, *DEFAULT_TEXT_SETUP, attacks_left_text, 1, 1.5, (255,255,160,255))

        phase_timer_color = (190,220,255,255) if boss.phase_timer > 19 else (180,160,225,255) if boss.phase_timer > 9 else (255,130,170,255) if boss.phase_timer > 4 else (255,88,88)
        last_phase_timer = basic_text_update(last_phase_timer, boss.phase_timer, phase_timer_text, 
                          str(boss.phase_timer).zfill(2), GAME_WIDTH-67.5, 16, *DEFAULT_TEXT_SETUP, phase_timer_text, 1, 1.5, phase_timer_color)
        
        last_score = basic_text_update(last_score, player.score, score_text, 
                          str(player.score).zfill(9), SIDEBAR_OFFSET_PLACEMENT, 138, *DEFAULT_TEXT_SETUP, score_text,  0.675, 1.25)
        
        last_highscore = basic_text_update(last_highscore, player.highscore, highscore_text, 
                          str(player.highscore).zfill(9), SIDEBAR_OFFSET_PLACEMENT, 98, *DEFAULT_TEXT_SETUP, highscore_text,  0.675, 1.25, (255, 255, 225))

        
        last_graze = basic_text_update(last_graze, player.graze, graze_text, 
                          str(player.graze), SIDEBAR_OFFSET_PLACEMENT, 378, *DEFAULT_TEXT_SETUP, graze_text,  0.75, 1.25, (217, 255, 236))

        if boss.health != last_boss_health:
            last_boss_health = boss.health
            boss_health_bar.width = max(0, min(boss_health_bar.max_width, int(boss_health_bar.max_width * boss.health/boss.phase_health)))
            boss_health_bar.build_image()


        if player.health != last_health or player.bombs != last_bombs:
            update_stars(player)
            last_health = player.health
            last_bombs = player.bombs

        if player.power != last_power:
            power_bar.width = max(0, min(power_bar.max_width, int(power_bar.max_width * (player.power / 128))))
            update_bars(player, power_bar_container,power_bar)

            power_text.empty()
            color = (255, 255, 255) if player.power < 125 else (195, 232, 255)
            text = str(int(player.power)) if player.power < 125 else "MAX"
            spacing = 1 if player.power < 125 else 1.25
            set_text(text, power_bar_container.x_pos + 24, 335, *DEFAULT_TEXT_SETUP, power_text, spacing, 1.25, color)

            last_power = player.power

        if boss.phase.name != last_spellcard_text and boss.phase.name is not None:
            spellcard_bar.x_pos = 470 + boss_spellcard_image.rect.centerx - spellcard_bar.width/2
            spellcard_bar.y_pos = boss_spellcard_image.rect.centery + spellcard_bar.height*2.65
            last_spellcard_text = update_spellcard_bar(spellcard_bar, boss, last_spellcard_text, boss.phase.name)
            set_spellcard_image(0.7, 255)
            boss_spellcard_image.rect.centerx = 470 + 500*0.7/2 # Add 500*0.7/2 because originally it's positioned by the topleft corner and not the center when rendered.

        if not boss.phase.is_spellcard and spellcard_bar.x_pos < 800:
            spellcard_background.alpha = lerp(spellcard_background.alpha, 0, 0.1)
            spellcard_background.image.set_alpha(int(spellcard_background.alpha))

            if spellcard_bar.x_pos < 800:
                spellcard_bar.x_pos += 15
                last_spellcard_text = update_spellcard_bar(spellcard_bar, boss, last_spellcard_text, (boss.phase.name, spellcard_bar.x_pos))

        if boss.phase.is_spellcard:
            if boss.spellcard_image_delay_over:
                set_spellcard_image(min(2, boss_spellcard_image.scale_factor + 0.04), max(0, boss_spellcard_image.alpha - 8))
                spellcard_bar.x_pos = lerp(spellcard_bar.x_pos, 220, 0.1)
                spellcard_bar.y_pos = lerp(spellcard_bar.y_pos, 37, 0.1)
                update_spellcard_bar(spellcard_bar, boss, last_spellcard_text, (boss.phase.name, spellcard_bar.x_pos))
            else:
                boss_spellcard_image.rect.centerx = lerp(boss_spellcard_image.rect.centerx, 270 + 500*0.7/2, 0.1)
                spellcard_bar.x_pos = lerp(spellcard_bar.x_pos, 470 - boss_spellcard_image.rect.width/2, 0.1)
                update_spellcard_bar(spellcard_bar, boss, last_spellcard_text, (boss.phase.name, spellcard_bar.x_pos))
                spellcard_background.alpha = lerp(spellcard_background.alpha, 150, 0.1)
                spellcard_background.image.set_alpha(int(spellcard_background.alpha))

        if screen == "menu":
            for letter in title_text:
                if random.randint(1,3) != 3:
                    continue
                Particle(random.randint(round(letter.x_pos), round(letter.x_pos+letter.image.get_width())), letter.y_pos+3, random.randint(20,40)/10, -random.randint(45,135), 1, 10, (255,255,255), option_bar.particles)

        if last_title_color_offset != title_color_offset:
            title_text.empty()
            set_text("TOUHOU EIKYUUTOUDO", 20, 20+title_color_offset/3, *DEFAULT_TEXT_SETUP, title_text, 1.2, 2.5, (200 + title_color_offset, 200 + title_color_offset, 255, 255), text_shadow=(3, 3, (220 - title_color_offset, 220 - title_color_offset, 255, 120)))
            set_text("PERMAFROST", 20+120, 70+title_color_offset/3, *DEFAULT_TEXT_SETUP, title_text, 1.2, 2.5, (200 + title_color_offset, 200 + title_color_offset, 255, 255), text_shadow=(3, 3, (220 - title_color_offset, 220 - title_color_offset, 255, 120)))
            last_title_color_offset = title_color_offset
        else:
            title_color_offset += title_color_offset_direction/2
            if title_color_offset >= 55:
                title_color_offset = 55
                title_color_offset_direction = -1
            elif title_color_offset <= 0:
                title_color_offset = 0
                title_color_offset_direction = 1

        if last_frost_aura_rotation != frost_aura.rotation_angle:
            frost_aura.image = pygame.transform.rotate(frost_aura.image_base, frost_aura.rotation_angle)
            frost_aura.rotation_angle -= 1
            frost_aura.rect = frost_aura.image.get_rect(center=cirno_portrait.rect.center)

        Particle(cirno_portrait.rect.centerx+50, cirno_portrait.rect.centery, random.randint(40,60)/10, random.randint(-55,55), 4, 4, (255,255,255), cirno_portrait_particles)
        Particle(cirno_portrait.rect.centerx-50, cirno_portrait.rect.centery, random.randint(40,60)/10, random.randint(180-55,180+55), 4, 4, (255,255,255), cirno_portrait_particles)
        Particle(cirno_portrait.rect.centerx, cirno_portrait.rect.centery, random.randint(40,60)/10, random.randint(0,360), 4, 4, (255,255,255), cirno_portrait_particles)
        for particle in cirno_portrait_particles:
            particle.loop()
            particle.speed = max(1, particle.speed-0.035)

        Particle(random.randint(round(option_bar.x_pos), round(option_bar.x_pos+option_bar.width)), option_bar.y_pos+3, random.randint(20,40)/10, -random.randint(45,135), 1, 10, (255,255,255), option_bar.particles)
        if random.randint(1,3) == 3:
            Particle(option_indicator.rect.centerx + option_bar.offset_direction*5, option_indicator.rect.centery, random.randint(20,40)/10, random.randint(165,195), 1, 10, (255,255,255), option_bar.particles)
        for particle in option_bar.particles:
            particle.loop()
        option_bar.offset += option_bar.offset_direction * 0.1

        if option_bar.offset >= 5:
            option_bar.offset = 5
            option_bar.offset_direction = -1
        elif option_bar.offset <= 0:
            option_bar.offset = 0
            option_bar.offset_direction = 1

        if screen == "menu":
            active_options = menu_options
            active_option = menu_option
        elif paused and screen == "game":
            active_options = pause_options
            active_option = pause_option
        else:
            active_options = None
            active_option = None

        if active_options is not None:
            option_bar.y_pos = active_options[active_option]["y"] + 35 + option_bar.offset
            option_indicator.rect.centerx = active_options[active_option]["x"] - 30 + option_bar.offset * 3

        option_bar.build_image()
        target_bar_alpha = 255 if screen == "menu" else (0 if not paused else 255)
        option_bar.alpha = lerp(option_bar.alpha, target_bar_alpha, 0.2)
        option_bar.image.set_alpha(round(option_bar.alpha))
        option_indicator.image.set_alpha(round(option_bar.alpha))
        for particle in option_bar.particles:
            particle.image.set_alpha(round(option_bar.alpha))
        
        if blackout_overlay.alpha_changing:
            screen_change_ready = False
            target_alpha = 255 if blackout_overlay.alpha_direction == 1 else 0
            blackout_overlay.alpha = lerp(blackout_overlay.alpha, target_alpha, 0.1)

            if abs(blackout_overlay.alpha - target_alpha) < 1:
                blackout_overlay.alpha = target_alpha
                if blackout_overlay.alpha_direction == -1:
                    blackout_overlay.alpha_changing = False
                elif blackout_overlay.will_change_screen:
                    screen_change_ready = True

                blackout_overlay.alpha_direction *= -1

            blackout_overlay.image.set_alpha(round(blackout_overlay.alpha))

        if screen == "game":
            pause_darken_overlay.alpha = lerp(pause_darken_overlay.alpha, 120 if paused else 0, 0.2)
            pause_darken_overlay.image.set_alpha(round(pause_darken_overlay.alpha))
            for letter in pause_options_text:
                letter.alpha = lerp(letter.alpha, 255 if paused else 0, 0.2)
                letter.image.set_alpha(letter.alpha)

        if screen_change_ready:
            play_bgm("game" if screen == "menu" else "menu")

            if screen == "menu":
                set_option(menu_option_index, menu_options, menu_options_keys, menu_options_text, menu_option_colors, "menu")
            elif paused and screen == "game":
                set_option(pause_option_index, pause_options, pause_options_keys, pause_options_text, pause_option_colors, "pause")

            screen = "game" if screen == "menu" else "menu"


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
                    else:
                        window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
                elif event.key == pygame.K_p:
                    paused = not paused
                    if paused:
                        pause_bgm()
                        set_option(pause_option_index, pause_options, pause_options_keys, pause_options_text, pause_option_colors, "pause")
                    else:
                        resume_bgm()
                        set_option(menu_option_index, menu_options, menu_options_keys, menu_options_text, menu_option_colors, "menu")

                elif event.key == pygame.K_m and not blackout_overlay.alpha_changing:
                    change_screen_setup()

                elif event.key in (pygame.K_UP, pygame.K_DOWN) and (screen == "menu" or paused):
                    if event.key == pygame.K_UP:
                        if menu_option_index > 0 and screen == "menu":
                            menu_option_index = set_option(menu_option_index - 1, menu_options, menu_options_keys, menu_options_text, menu_option_colors, "menu")
                        elif pause_option_index > 0 and paused:
                            pause_option_index = set_option(pause_option_index - 1, pause_options, pause_options_keys, pause_options_text, pause_option_colors, "pause")                            
                    elif event.key == pygame.K_DOWN:
                        if menu_option_index < len(menu_options_keys)-1 and screen == "menu":
                            menu_option_index = set_option(menu_option_index + 1, menu_options, menu_options_keys, menu_options_text, menu_option_colors, "menu")
                        elif pause_option_index < len(pause_options_keys)-1 and paused:
                            pause_option_index = set_option(pause_option_index + 1, pause_options, pause_options_keys, pause_options_text, pause_option_colors, "pause")                            

                elif event.key in (pygame.K_SPACE, pygame.K_RETURN) and not blackout_overlay.alpha_changing and screen == "menu":
                    if menu_option == "Start":
                        change_screen_setup()
                        if screen == "menu" or screen == "game":
                            boss.pause_time = 30
                    if menu_option == "Quit":
                        running = False
            if event.type == pygame.MOUSEMOTION and blackout_overlay.alpha < 50:
                if screen == "menu":
                    mouse_selection_change(event, menu_options, menu_options_keys, menu_option_index, menu_options_text, menu_option_colors, "menu")
                elif paused:
                    mouse_selection_change(event, pause_options, pause_options_keys, pause_option_index, pause_options_text, pause_option_colors, "pause")

                    
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not blackout_overlay.alpha_changing:
                if screen == "menu":
                    if menu_option == "Start":
                        change_screen_setup()
                    elif menu_option == "Quit":
                        running = False


                
        if not paused and not screen=="menu":
            player.loop(boss)
            boss.loop(player)
        draw(window, player, boss)


    pygame.quit()



if __name__ == "__main__":

    main(window)