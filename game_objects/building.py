import pygame
from game_objects.game_object import Game_Object
from core.func import *
from core.image_transform import *
from game_objects.cable import *
from hud_elements.button import *
import numpy as np



class Building(Game_Object):
    def __init__(self, game, team, name, slot, hp = 1000, image = None, size = [1,1]):
        super().__init__(game,team, name = name, slot = slot, hp = hp, size = size)
        self.type = "building"
        self.image = image
        self.cable = None
        self.static_cables = []
        if self.image != None:
            print(team)
            self.image = colorize_alpha(image, pygame.Color(team[0], team[1], team[2]), 50)

        self.buttons = [
        #Button(self.game_ref, self, 0.5,9, self.team, self.game_ref.images["leg"], oneshot = True, oneshot_func = create_cable, )
        Button(self.game_ref, self, 0.5,1, self.team, self.game_ref.images["homo"], oneshot = True, oneshot_func = self.purchase, argument = "Soldier")
        ]



    def create_cable(self):
        x,y = self.slot_to_pos()
        if "mouse1" in self.game_ref.keypress:
            if point_inside(self.game_ref.mouse_pos, [x,y], self.size):
                if self.cable == None and self.active == True:
                    self.cable = Cable(self.game_ref, self.team, self.game_ref.GT)
                    self.cable.generate([x,y], self.game_ref.mouse_pos, 45,3)
                else:
                    self.cable = None


            else:
                self.cable = None
            # else:
            #
            #     for obj in self.game_ref.render_layers["3.BUILDINGS"]:
            #         if obj.team == self.team and point_inside(self.game_ref.mouse_pos, obj.slot_to_pos(), obj.size):
            #             self.cable = None
            #
            #
            #             cable_temp = Cable(self.team, self.game_ref.GT)
            #             cable_temp.generate(self.slot_to_pos(), obj.slot_to_pos(), 45,3)
            #             self.static_cables.append(cable_temp)
            #             print("Created static cable")
            #             break





    def tick_cable(self):
        if self.cable != None:
            self.cable.startpoint.pos = np.array(self.slot_to_pos_c_cam())
            self.cable.endpoint.pos = np.array(self.game_ref.mouse_pos)
            self.cable.tick()
            if "mouse1" in self.game_ref.keypress:
                for obj in self.game_ref.render_layers["3.BUILDINGS"]:
                    if obj != self and obj.team == self.team and point_inside(self.game_ref.mouse_pos, obj.slot_to_pos(), obj.size):
                        self.cable = None


                        cable_temp = Cable(self.game_ref, self.team, self.game_ref.GT)
                        cable_temp.generate(self.slot_to_pos_c_cam(), obj.slot_to_pos_c_cam(), 10,3)
                        self.game_ref.render_layers["5.CABLE"].append(cable_temp)
                        print("Created static cable")
                        break










    def tick(self):

        self.click()


        if self.active:
            if "esc" in self.game_ref.keypress:
                self.activate(False)

        self.render()
        self.tick_buttons()
        self.tick_cable()
        self.create_cable()
