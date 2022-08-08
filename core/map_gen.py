import pygame
import random


def gen_map(image):
    pxarray = pygame.PixelArray(image.copy())
    tiles = []
    deposits = []
    mines = []
    size = pxarray.shape
    for y in range(size[1]):
        for x in range(size[0]):
            if pxarray[x, y] == 0:
                tiles.append([x, y])
            elif pxarray[x, y] == image.map_rgb((0, 255, 0)):
                deposits.append([x, y])

    i = 0
    while i < 7:
        x = random.randint(0, size[0]-1)
        y = random.randint(0, size[1]-1)
        if pxarray[x,y] == image.map_rgb((255, 255, 255)):
            mines.append([x,y])
            i+=1

    print(mines)
    return size, tiles, deposits, mines
