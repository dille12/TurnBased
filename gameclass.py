import pygame
from texture.texture import load_images
from values import *
import sys
from core.keypress import *
from core.func import *


class Game:

    """
    Game class to contain all information for ease of access.
    """

    def __init__(self, resolution):

        pygame.init()
        pygame.font.init()

        self.images = {}
        self.terminal = {}
        self.size_conv = [1920/resolution[0], 1080/resolution[1]]
        self.screen = pygame.display.set_mode(resolution)
        load_images(self ,self.size_conv)
        print(self.images)

        self.clock = pygame.time.Clock()

        self.render_layers = {}
        self.camera_pos = [0,0]
        self.keypress = []
        self.keypress_held_down = []


    def get_pos(self,pos):
        return minus(pos,self.size_conv, op = "/")


    def loop(self):

        while 1:
            self.clock.tick(60)
            key_press_manager(self)
            self.screen.fill(BLACK)
            render_text(self, "RUNKKARI", self.mouse_pos, 99)
            pygame.display.update()
