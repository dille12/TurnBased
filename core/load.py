from texture.texture import load_images
from sounds.sounds import load_sounds
import pygame
from core.map_gen import *
from game_objects.wall import *
from game_objects.deposit import *
from game_objects.mine import *
import gamestates.menu
from hud_elements.textbox import TextBox
import time


def load(game):
    game.loading = "Images"
    load_images(game, game.size_conv)
    game.loading = "Sounds"
    load_sounds(game)
    game.loading = "Map"

    game.map_size = game.images["map"].get_size()
    game.los_image = pygame.Surface(game.images["map"].get_size()).convert()
    game.los_image.fill([0, 0, 0])
    # game.los_image.set_alpha(100)
    game.los_image.set_colorkey([255, 255, 255])

    gen_map(game, game.images["layout"])

    for x in game.deposits:
        game.render_layers["1.BOTTOM"].append(Deposit(game, nature, "Wall", x))
    game.mine_positions = []

    for x in game.tiles:
        game.render_layers["1.BOTTOM"].append(Wall(game, nature, "Wall", x))

    game.chat.chatbox = TextBox(game, [game.resolution[0]-200,90], "", size = 35)

    game.loading = "Complete"
    print(f"LOADABLE_OBJECTS: {game.load_i}")

    game.state = gamestates.menu.Menu(game)
