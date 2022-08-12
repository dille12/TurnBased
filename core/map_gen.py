import pygame
import random
import core.func
from game_objects.mine import Mine
from values import *


def gen_map(game, image):
    game.map_layout = image
    game.pxarray = pygame.PixelArray(image.copy())
    tiles = []
    deposits = []
    mines = []
    size = game.pxarray.shape
    for y in range(size[1]):
        for x in range(size[0]):
            if game.pxarray[x, y] == 0:
                tiles.append([x, y])
            elif game.pxarray[x, y] == image.map_rgb((0, 255, 0)):
                deposits.append([x, y])


    game.size_slots = size
    game.tiles = tiles
    game.deposits = deposits


def random_gen_mines(game):

    mines = []
    i = 0
    while i < 7:
        x = random.randint(0, game.size_slots[0] - 1)
        y = random.randint(0, game.size_slots[1] - 1)
        if [x, y] in mines:
            continue
        if game.pxarray[x, y] == game.map_layout.map_rgb((255, 255, 255)):
            mines.append([x, y])
            i += 1
    core.func.pick_random_from_list(mines).append("Iridium")

    for x in mines:
        if len(x) == 2:
            x.append(
                core.func.pick_random_from_list(["Gallium", "Uranium", "Tungsten"])
            )

    game.mines = mines


def gen_mines(game):
    print("Generating mines")
    print(game.mines)
    for x, y, ore in game.mines:
        mine = Mine(game, nature, "Wall", [x, y])
        mine.resource = ore
        game.render_layers["1.BOTTOM"].append(mine)
        game.mine_positions.append([x, y])
