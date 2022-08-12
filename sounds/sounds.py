import pygame
import os
from os import listdir
from os.path import isfile, join


def load_sounds(game):

    for path in ["files", "music"]:

        mypath = os.path.abspath(os.getcwd()) + f"/sounds/{path}/"
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        for x in onlyfiles:
            try:
                sound = pygame.mixer.Sound(f"sounds/{path}/{x}")
                sound.set_volume(game.sound_volume)
                game.loading = f"{path}/{x}"
                game.sounds[x.removesuffix(".mp3")] = sound
                game.load_i += 1
            except Exception as e:
                print(e)


# if __name__ == "__main__":
#     load_images(game, 1)
