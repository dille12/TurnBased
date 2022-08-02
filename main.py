import pygame
from texture.texture import load_images
from sounds.sounds import load_sounds
from game_objects.game_object import *
from game_objects.npc import *
from game_objects.building import *
from game_objects.wall import *
from values import *
import sys
from core.keypress import *
from core.camera_movement import *
from core.func import *
from core.map_gen import *
import numpy as np
from game_objects.objects import *
from core.player import Player


class Game:

    """
    Game class to contain all information for ease of access.
    """

    def __init__(self, resolution):
        pygame.init()
        pygame.font.init()

        self.GT = GameTick

        self.resolution = resolution


        self.images = {}
        self.sounds = {}
        self.terminal = {}
        self.size_conv = [1920/resolution[0], 1080/resolution[1]]

        self.player_team = blue_t

        self.qsc = 1920/resolution[0]

        self.ss = 100 * self.qsc #SLOT SIZE

        self.screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
        load_images(self ,self.size_conv)
        load_sounds(self)
        print(self.images)
        print(self.sounds)

        self.clock = pygame.time.Clock()

        tiles = gen_map(self.images["layout"])

        self.render_layers = {"1.BOTTOM" : [], "2.ORE" : [], "3.BUILDINGS" : [], "4.NPCS" : [], "5.CABLE" : [], "6.HUD" : []}
        #self.render_layers["3.BUILDINGS"].append(Building(self,GREEN,"Base",[3,3], image = self.images["base"].copy(), size = [2,2]))
        self.render_layers["3.BUILDINGS"].append(Base(self, blue_t, [1,1]))
        self.render_layers["3.BUILDINGS"].append(ElectricTower(self, blue_t, [5,2]))
        self.render_layers["3.BUILDINGS"].append(ElectricTower(self, blue_t, [9,2]))

        self.render_layers["4.NPCS"].append(Builder(self, blue_t, [0,0]))


        for x in tiles:
            self.render_layers["1.BOTTOM"].append(Wall(self,BLACK,"Wall",x))


        self.camera_pos = [0,0]
        self.prev_pos = [0,0]
        self.camera_pos_target = [0,0]
        self.keypress = []
        self.keypress_held_down = []
        self.cam_moving = False
        self.timedelta = 1
        self.activated_object = None
        self.fps = 0

    def get_pos(self,pos):
        #return minus(pos,self.camera_pos, op = "-")
        return minus(minus(pos,self.camera_pos, op = "-"),self.size_conv, op = "/")

    def gen_object(self, type, team, slot):
        print("Generating in", slot)
        if type == "Soldier":
            self.render_layers["4.NPCS"].append(Soldier(self, team, slot))

    def renderobjects(self):

        self.screen.blit(self.images["map"], minus([0,0],self.camera_pos, op="-"))

        for x in self.render_layers.keys():
            for obj in self.render_layers[x]:
                obj.tick()



    def return_objects(self):
        objects = []
        for x in self.render_layers.keys():
            for obj in self.render_layers[x]:
                objects.append(obj)

        return objects




    def get_occupied_slots(self):

        slots = []
        for x in self.render_layers.keys():
            for obj in self.render_layers[x]:
                for x in range(obj.slot_size[0]):
                    for y in range(obj.slot_size[1]):
                        if core.func.minus(obj.slot,[x,y]) not in slots:
                            slots.append(core.func.minus(obj.slot,[x,y]))
        return slots


    def draw_HUD(self):
        if self.activated_object != None:
            render_text(self, self.activated_object.name, [20,20], 60, color = self.activated_object.team.color)
            if self.activated_object.type == "npc":
                render_text(self, f"Movement : {self.activated_object.turn_movement}/{self.activated_object.movement_range}", [20,70], 30, color = self.activated_object.team.color)
                render_text(self, f"Mode : {self.activated_object.mode}", [20,100], 30, color = self.activated_object.team.color)








    def loop(self):
        key_press_manager(self)
        cam_movement(self)
        self.delta = np.array(self.prev_pos) - np.array(self.camera_pos)
        self.prev_pos = self.camera_pos.copy()

        #self.camera_pos = minus(self.mouse_pos,[0.3,0.3], op = "*")
        self.screen.fill(BLACK)
        self.renderobjects()
        self.draw_HUD()

        print_s(self, f"FPS:{self.fps}", 1)

        pygame.display.update()
