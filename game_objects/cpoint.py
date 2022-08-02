import pygame
from game_objects.game_object import Game_Object
from core.func import *
from core.image_transform import *


class CapPoint(Game_Object):
    def __init__(self, game, team, name, slot, hp = 1000, image = None, size = [1,1]):
        super().__init__(game,team, name = name, slot = slot, hp = hp, size = size)
        self.type = "building"
        self.image = image
        if self.image != None:
            print(team)
            self.image = colorize_alpha(image, pygame.Color(team[0], team[1], team[2]), 50)


    def tick(self):

        self.click()


        if self.active:
            if "esc" in self.game_ref.keypress:
                self.activate(False)



        self.render()
