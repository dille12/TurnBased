import pygame
from texture.texture import load_images
from sounds.sounds import load_sounds
from game_objects.game_object import *
from game_objects.npc import *
from game_objects.wall import *
from values import *
import sys
from core.keypress import *
from core.camera_movement import *
from core.func import *
from core.map_gen import *


class Game:

    """
    Game class to contain all information for ease of access.
    """

    def __init__(self, resolution):
        pygame.init()
        pygame.font.init()

        self.GT = GameTick


        self.images = {}
        self.sounds = {}
        self.terminal = {}
        self.size_conv = [1920/resolution[0], 1080/resolution[1]]
        self.screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
        load_images(self ,self.size_conv)
        load_sounds(self)
        print(self.images)
        print(self.sounds)

        self.clock = pygame.time.Clock()

        tiles = gen_map(self.images["layout"])

        self.render_layers = {"1.BOTTOM" : [], "2.ORE" : [], "3.BUILDINGS" : [], "4.NPCS" : [], "5.HUD" : []}
        self.render_layers["4.NPCS"].append(NPC(self,GREEN,"HOMO",[1,1], image = self.images["homo"].copy()))
        self.render_layers["4.NPCS"].append(NPC(self,BLUE, "HOMO",[2,2], image = self.images["homo"].copy()))


        for x in tiles:
            self.render_layers["1.BOTTOM"].append(Wall(self,BLACK,"Wall",x))


        self.camera_pos = [0,0]
        self.camera_pos_target = [0,0]
        self.keypress = []
        self.keypress_held_down = []
        self.cam_moving = False
        self.timedelta = 1
        self.activated_object = None

    def get_pos(self,pos):
        #return minus(pos,self.camera_pos, op = "-")
        return minus(minus(pos,self.camera_pos, op = "-"),self.size_conv, op = "/")

    def renderobjects(self):

        self.screen.blit(self.images["map"], minus([0,0],self.camera_pos, op="-"))

        for x in self.render_layers.keys():
            for obj in self.render_layers[x]:
                obj.tick()


    def get_occupied_slots(self):

        slots = []
        for x in self.render_layers.keys():
            for obj in self.render_layers[x]:
                if obj.slot not in slots:
                    slots.append(obj.slot)
        return slots


    def draw_HUD(self):
        if self.activated_object != None:
            render_text(self, self.activated_object.name, [20,20], 60, color = self.activated_object.team)
            render_text(self, f"Movement : {self.activated_object.turn_movement}/{self.activated_object.movement_range}", [20,70], 30, color = self.activated_object.team)
            






    def loop(self):
        key_press_manager(self)
        cam_movement(self)
        #self.camera_pos = minus(self.mouse_pos,[0.3,0.3], op = "*")
        self.screen.fill(BLACK)
        self.renderobjects()
        self.draw_HUD()
        pygame.display.update()
