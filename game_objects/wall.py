import pygame
from game_objects.game_object import Game_Object
from core.func import *
from core.image_transform import *

class Wall(Game_Object):
    def __init__(self, game, team, name, slot, movement_range = 3, hp = 100, image = None):
        super().__init__(game,team, name = name, slot = slot, hp = hp)


    def tick(self):
        pass
