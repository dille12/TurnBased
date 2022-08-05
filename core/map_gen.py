import pygame


def gen_map(image):
    pxarray = pygame.PixelArray(image.copy())
    tiles = []
    deposits = []
    size = pxarray.shape
    for y in range(size[1]):
        for x in range(size[0]):
            if pxarray[x, y] == 0:
                tiles.append([x, y])
            elif pxarray[x, y] == image.map_rgb((0, 255, 0)):
                deposits.append([x, y])

    print(deposits)
    return size, tiles, deposits
