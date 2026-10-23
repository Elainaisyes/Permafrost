import pygame

BACKGROUND_MUSIC = {
    "menu": {"path": "assets/audios/bgm/Echos of Distant Days.mp3", "volume": 0.5, "last_position": 0.0},
    "game": {"path": "assets/audios/bgm/UN-Owen-Was-Her.mp3", "volume": 0.75, "last_position": 0.0},
    "gameover": {"path": "assets/audios/bgm/sins 13.mp3", "volume": 1.25, "last_position": 0.0}
}

current_track = None
start_offset = 0.0

def play_sound(sound, volume = 1):
    sound.set_volume(volume)
    sound.play()

def get_current_position():
    if not current_track:
        return 0.0

    played_ms = pygame.mixer.music.get_pos()
    if played_ms == -1: 
        return 0.0
    return start_offset + played_ms / 1000

def play_bgm(track_key, loops=-1, start = 0.0, fade_ms=2000, resume=True):
    global current_track, start_offset

    if current_track == track_key and not pygame.mixer.music.get_busy() and resume:
        pygame.mixer.music.unpause()
        return

    if current_track and current_track != track_key:
        BACKGROUND_MUSIC[current_track]["last_position"] = get_current_position()

    track = BACKGROUND_MUSIC[track_key]
    current_track = track_key

    start_pos = track["last_position"] if resume else start
    start_offset = start_pos

    pygame.mixer.music.load(track["path"])
    pygame.mixer.music.set_volume(track["volume"])
    pygame.mixer.music.play(loops=loops, start=start_pos, fade_ms=fade_ms)

def pause_bgm(fadeout_ms=750):
    global current_track, start_offset
    if current_track:
        pos = get_current_position()+fadeout_ms/1000
        BACKGROUND_MUSIC[current_track]["last_position"] = pos
        start_offset = pos
        pygame.mixer.music.fadeout(fadeout_ms)

def resume_bgm():
    global current_track
    if current_track:
        track = BACKGROUND_MUSIC[current_track]
        pos = start_offset
        pygame.mixer.music.load(track["path"])
        pygame.mixer.music.set_volume(track["volume"])
        pygame.mixer.music.play(loops=-1, start=pos, fade_ms=400)

def reset_track_position(track_key):
    BACKGROUND_MUSIC[track_key]["last_position"] = 0.0