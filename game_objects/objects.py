from game_objects.game_object import Game_Object
from game_objects.npc import NPC
from game_objects.building import Building

import pygame
from core.func import *
from core.image_transform import *
from hud_elements.button import *

class Soldier(NPC):
    def __init__(self, game, team, slot):
        hp = 100
        name = "Soldier"
        image = game.images["soldier"].copy()
        movement_range = 3
        self.range = 2

        super().__init__(game, team, name, slot, movement_range = movement_range, hp = hp, image = image)

        self.buttons = [
        Button(self.game_ref, self, 0.5,9, self.team.color, self.game_ref.images["leg"], activator = "walk", active = True, key_press = "a"),
        Button(self.game_ref, self, 2,9, self.team.color, self.game_ref.images["fist"], activator = "attack", key_press = "s"),
        Button(self.game_ref, self, 3.5,9, self.team.color, self.game_ref.images["shield"], activator = "defend", key_press = "d")
        ]
        self.check_mode()


class Builder(NPC):
    def __init__(self, game, team, slot):
        hp = 50
        name = "Builder"
        image = game.images["builder"].copy()
        movement_range = 3
        self.range = 1


        super().__init__(game, team, name, slot, movement_range = movement_range, hp = hp, image = image)

        self.buttons = [
        Button(self.game_ref, self, 0.5,9, self.team.color, self.game_ref.images["leg"], activator = "walk", active = True, key_press = "a"),
        Button(self.game_ref, self, 2,9, self.team.color, self.game_ref.images["fist"], activator = "attack", key_press = "s")
        # Button(self.game_ref, self, 3.5,9, self.team.color, self.game_ref.images["shield"], activator = "defend", key_press = "d")
        ]
        self.check_mode()


class Base(Building):
    def __init__(self, game, team, slot):
        hp = 1000
        name = "Base"
        image = game.images["base"].copy()
        size = [2,2]
        self.range = 0

        super().__init__(game, team, name, slot, size = size, hp = hp, image = image)

        self.buttons = [
        #Button(self.game_ref, self, 0.5,9, self.team.color, self.game_ref.images["leg"], oneshot = True, oneshot_func = create_cable, )
        Button(self.game_ref, self, 0.5,1, self.team.color, self.game_ref.images["soldier"], oneshot = True, oneshot_func = self.purchase, argument = "Soldier")
        ]
        if self.team == self.game_ref.player_team:
            self.center()


class ElectricTower(Building):
    def __init__(self, game, team, slot):
        hp = 200
        name = "Electric Tower"
        image = game.images["elec_tower"].copy()
        size = [1,1]
        self.range = 0

        super().__init__(game, team, name, slot, size = size, hp = hp, image = image)
