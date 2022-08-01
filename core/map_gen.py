import pygame


def gen_map(image):
    pxarray =  pygame.PixelArray(image.copy())
    tiles = []
    size = pxarray.shape
    for y in range(size[1]):
        for x in range(size[0]):
            if pxarray[x,y] == 0:
                tiles.append([x,y])
    print(tiles)
    return tiles
