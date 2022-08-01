import pygame
from game_objects.game_object import Game_Object
from core.func import *
from core.image_transform import *

class NPC(Game_Object):
    def __init__(self, game, team, name, slot, movement_range = 3, hp = 100, image = None):
        super().__init__(game,team, name = name, slot = slot, hp = hp)

        self.movement_range = movement_range
        self.turn_movement = movement_range
        self.routes = []
        self.moving_route = []
        self.move_tick = game.GT(20)
        self.target = None
        self.image = image
        if self.image != None:
            print(team)
            self.image = colorize_alpha(image, pygame.Color(team[0], team[1], team[2]), 100)



    def move(self):

        if self.target == None:
            self.target = self.slot.copy()

        if self.move_tick.tick():
            self.slot = self.target.copy()
            self.moving_route.remove(self.moving_route[0])
            if self.moving_route == []:
                return
            self.target = self.moving_route[0]

            list_play([self.game_ref.sounds["walk1"], self.game_ref.sounds["walk2"], self.game_ref.sounds["walk3"]])

            self.turn_movement -= 1

            print(self.moving_route)
        else:
            self.slot = minus(self.slot, minus(minus(self.target, self.slot, op = "-"), [0.6,0.6], op="*"))





    def tick(self):
        if self.moving_route == []:
            self.click()

        if self.active and "mouse0" in self.game_ref.keypress:
            self.routes = self.scan_movement(self.turn_movement)

        if self.active:

            self.render_routes()


            if "esc" in self.game_ref.keypress:
                self.activate(False)

        if self.moving_route != []:
            self.move()


        self.render()
