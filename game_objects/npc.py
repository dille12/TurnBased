import pygame
from game_objects.game_object import Game_Object
from core.func import *
from core.image_transform import *
from hud_elements.button import *

class NPC(Game_Object):
    def __init__(self, game, team, name, slot, movement_range = 3, hp = 100, image = None):
        super().__init__(game,team, name = name, slot = slot, hp = hp)
        self.type = "npc"
        self.movement_range = movement_range
        self.turn_movement = movement_range
        self.routes = []
        self.moving_route = []
        self.move_tick = game.GT(20)
        self.target = None
        self.image = image
        self.build = None
        if self.image != None:
            self.image = colorize_alpha(image.copy(), pygame.Color(self.team.color[0], self.team.color[1], self.team.color[2]), 50)
            self.image_bg = colorize_alpha(image.copy(), pygame.Color(0,0,0), 100)



        self.check_mode()


    def npc_build(self, type):
        print("Building")

        self.occ_slots = self.game_ref.get_occupied_slots()

        #if type == "elec_tower":
        self.build = type
        self.build.c_building = True





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

        if self.build == None:

            if self.mode == "walk":

                if self.active and "mouse0" in self.game_ref.keypress:
                    self.routes = self.scan_movement(self.turn_movement)

                if self.active:
                    self.render_routes()

            elif self.mode == "attack" and self.active and self.shots > 0:
                x,y = self.slot_to_pos_c(minus(self.slot,[-self.range, -self.range]))
                size = (1 + self.range * 2) * self.game_ref.ss


                pygame.draw.rect(self.game_ref.screen, [255,0,0], [x,y,size,size],2)

                self.highlight_enemies()




        if "esc" in self.game_ref.keypress:
            self.activate(False)

        if self.moving_route != []:
            self.move()


        self.render()

        if self.build != None:

            self.build.tick_buildable(self.occ_slots)

            if "mouse0" in self.game_ref.keypress and self.build.able_to_place:
                self.game_ref.gen_object(self.build)
                self.build = None

        else:

            self.tick_buttons()