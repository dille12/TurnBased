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

        self.select_sound = game.sounds["select_sold"]

        super().__init__(game, team, name, slot, movement_range = movement_range, hp = hp, image = image)

        self.buttons = [
        Button(self.game_ref, self, 0.5,9, self.team.color, self.game_ref.images["leg"], activator = "walk", active = True, key_press = "a"),
        Button(self.game_ref, self, 2,9, self.team.color, self.game_ref.images["fist"], activator = "attack", key_press = "s"),
        Button(self.game_ref, self, 3.5,9, self.team.color, self.game_ref.images["shield"], activator = "defend", key_press = "d")
        ]
        self.check_mode()

    def copy(self):
        return Soldier(self.game_ref, self.team, self.slot)


class Builder(NPC):
    def __init__(self, game, team, slot):
        hp = 50
        name = "Builder"
        image = game.images["builder"].copy()
        movement_range = 3
        self.range = 1

        self.select_sound = game.sounds["select_builder"]


        super().__init__(game, team, name, slot, movement_range = movement_range, hp = hp, image = image)

        self.buttons = [
        Button(self.game_ref, self, 0.5,9, self.team.color, self.game_ref.images["leg"], activator = "walk", active = True, key_press = "a"),
        Button(self.game_ref, self, 2,9, self.team.color, self.game_ref.images["fist"], activator = "attack", key_press = "s"),
        Button(self.game_ref, self, 0.5,2, self.team.color, self.game_ref.images["elec_tower"], oneshot = True, oneshot_func = self.npc_build, argument = ElectricTower(self.game_ref, self.team, [-1,-1]))
        # Button(self.game_ref, self, 3.5,9, self.team.color, self.game_ref.images["shield"], activator = "defend", key_press = "d")
        ]
        self.check_mode()
    def copy(self):
        return Builder(self.game_ref, self.team, self.slot)


class Base(Building):
    def __init__(self, game, team, slot):
        hp = 1000
        name = "Base"

        self.select_sound = game.sounds["select_base"]

        print("BASE: type", type(self).__dict__)

        image = game.images["base"].copy()
        size = [2,2]
        self.range = 0

        super().__init__(game, team, name, slot, size = size, hp = hp, image = image)

        self.buttons = [
        #Button(self.game_ref, self, 0.5,9, self.team.color, self.game_ref.images["leg"], oneshot = True, oneshot_func = create_cable, )
        Button(self.game_ref, self, 0.5,1, self.team.color, self.game_ref.images["soldier"], oneshot = True, oneshot_func = self.purchase, argument = Soldier(self.game_ref, self.team, [-1,-1]))
        ]
        if self.team == self.game_ref.player_team:
            print("CENTERING IN START")
            self.center()
    def copy(self):
        return Base(self.game_ref, self.team, self.slot)


class ElectricTower(Building):
    def __init__(self, game, team, slot):
        hp = 200
        name = "Electric Tower"
        image = game.images["elec_tower"].copy()
        self.select_sound = game.sounds["select_tower"]
        size = [1,1]
        self.range = 0

        super().__init__(game, team, name, slot, size = size, hp = hp, image = image)

    def copy(self):
        return ElectricTower(self.game_ref, self.team, self.slot)
