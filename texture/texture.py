import pygame
import os
from os import listdir
from os.path import isfile, join

def load_images(game, size_conversion):

    for path in ["sprites", "non_alpha"]:

        mypath = os.path.abspath(os.getcwd()) + f"/texture/{path}/"
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        for x in onlyfiles:
            if path == "sprites":
                temp = pygame.image.load(f"{mypath}/{x}").convert_alpha()
            else:
                temp = pygame.image.load(f"{mypath}/{x}").convert()
            size = temp.get_size()
            print(size)
            image = pygame.transform.scale(temp, [size[0]/size_conversion[0], size[1]/size_conversion[1]])
            game.images[x.removesuffix(".png")] = image



    for x in range(1,151):
        game.terminal[x] = pygame.font.Font('texture/terminal.ttf', round(x/size_conversion[0]))


# if __name__ == "__main__":
#     load_images(game, 1)
