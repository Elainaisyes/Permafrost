import pygame, time

BACKGROUND_MUSIC = {
    "menu": {"path": "assets/audios/bgm/Echos of Distant Days.mp3", "volume": 0.5, "last_position": 0.0},
    "game": {"path": "assets/audios/bgm/UN-Owen-Was-Her.mp3", "volume": 0.75, "last_position": 0.0},
    "game_alternate": {"path": "assets/audios/bgm/Septette for the Dead Princess.mp3", "volume": 1, "last_position": 0.0},
    "gameover": {"path": "assets/audios/bgm/sins 13.mp3", "volume": 1, "last_position": 0.0}
}

current_track = None
start_offset = 0.0

def play_sound(sound, volume = 1):
    sound.set_volume(volume)
    sound.play()


#time.monotonic() used to calculate the amount of milliseconds elapsed since the last time position update.
def get_current_position():
    global current_track

    if not current_track:
        return 0.0

    track = BACKGROUND_MUSIC[current_track]

    if not pygame.mixer.music.get_busy():
        return track["last_position"]

    elapsed = time.monotonic() - track["last_position_time"]
    return track["last_position"] + elapsed

def play_bgm(track_key, loops=-1, start=0.0, fade_ms=2000, resume=True):
    global current_track

    if current_track == track_key and not pygame.mixer.music.get_busy() and resume:
        pygame.mixer.music.unpause()
        return

    if current_track and current_track != track_key:
        track = BACKGROUND_MUSIC[current_track]
        track["last_position"] = get_current_position()
        track["last_position_time"] = time.monotonic()

    track = BACKGROUND_MUSIC[track_key]
    current_track = track_key

    if resume:
        pos = track["last_position"]
    else:
        pos = start
        track["last_position"] = pos

    track["last_position_time"] = time.monotonic()

    pygame.mixer.music.load(track["path"])
    pygame.mixer.music.set_volume(track["volume"])
    pygame.mixer.music.play(loops=loops, start=pos, fade_ms=fade_ms)

def pause_bgm(fadeout_ms=750):
    global current_track
    if current_track:
        track = BACKGROUND_MUSIC[current_track]
        track["last_position"] = get_current_position()
        track["last_position_time"] = time.monotonic()
        pygame.mixer.music.fadeout(fadeout_ms)

def resume_bgm():
    global current_track
    if current_track:
        track = BACKGROUND_MUSIC[current_track]
        pos = track["last_position"]
        track["last_position_time"] = time.monotonic()

        pygame.mixer.music.load(track["path"])
        pygame.mixer.music.set_volume(track["volume"])
        pygame.mixer.music.play(loops=-1, start=pos, fade_ms=400)


def reset_track_position(track_key):
    BACKGROUND_MUSIC[track_key]["last_position"] = 0.0