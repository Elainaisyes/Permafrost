import pygame

def play_sound(sound, volume = 1):
    sound.set_volume(volume)
    sound.play()