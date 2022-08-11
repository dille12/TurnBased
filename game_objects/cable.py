from game_objects.game_object import Game_Object
import pygame
import numpy as np
from core.func import *
import time
import math
import random

class Cable(Game_Object):
    def __init__(self, game, team, game_tick, dont_freeze = False):

        super().__init__(game, team)

        self.points = []
        self.sticks = []

        self.camera_pos = np.array([0, 0])
        self.game_ref = game
        self.slot_size = [0, 0]
        self.slot = [-1, -1]
        self.type = "cable"
        self.freeze_tick = game_tick(150, oneshot = True)
        self.dont_freeze = dont_freeze
        self.frozen = False
        self.connected = True

    def __str__(self):
        return f"Cable {self.start_obj} {self.end_obj}"

    def tick(self, color_override = False, ignore_camera = False):

        self.camera_pos = self.game_ref.delta if not ignore_camera else [0,0]
        self.Simulate()

        for x in self.sticks:

            x.render(
                self.game_ref.screen,
                self.team if not color_override else color_override
            )

    def update(self):
        if self.start_obj.connected_to_base and not self.end_obj.connected_to_base:
            self.end_obj.connected_to_base = True
            print(self.end_obj)
            self.game_ref.connected_in_scan += 1
            self.connected = True
        elif self.end_obj.connected_to_base and not self.start_obj.connected_to_base:
            self.start_obj.connected_to_base = True
            print(self.start_obj)
            self.game_ref.connected_in_scan += 1
            self.connected = True

        elif self.end_obj.connected_to_base and self.start_obj.connected_to_base:
            self.connected = True

    def disconnect(self):
        self.connected = False
        self.start_obj.connected_to_base = False
        self.end_obj.connected_to_base = False

    def connect(self, boolean=True):
        if not self.start_obj.connected_to_base or not self.end_obj.connected_to_base:
            self.connected = True
            self.start_obj.connected_to_base = boolean
            print(self.start_obj)
            self.end_obj.connected_to_base = boolean
            print(self.end_obj)
            self.game_ref.connected_in_scan += 2

    def generate(self, start, end, hanging, subdiv=2, start_obj=None, end_obj=None):
        print("Starting generation")
        self.points.append(Point(np.array(start), True))
        self.startpoint = self.points[-1]
        self.points.append(Point(np.array(end), True))
        self.endpoint = self.points[-1]


        self.sticks.append(Stick(self, self.points[0], self.points[1], self.game_ref))

        for x in range(subdiv):
            sticks2 = self.sticks.copy()
            for stick in sticks2:
                stick.subdivide(self.points, self.sticks, lower_center=hanging)

        self.start_obj = start_obj
        self.end_obj = end_obj

        for x in self.sticks:
            for y in self.sticks:
                if x.point1 in [y.point1, y.point2] or x.point2 in [y.point1, y.point2]:
                    x.connected_sticks.append(y)

                if self.start_obj == None or self.end_obj == None:
                    continue


                if self.startpoint in [x.point1, x.point2]:
                    self.start_obj.connected_cables.append(x)
                    x.start_object = self.start_obj
                if self.endpoint in [x.point1, x.point2]:
                    self.end_obj.connected_cables.append(x)
                    x.start_object = self.end_obj


        print("Cable generated")
        return self

    def Simulate(self):
        for point in self.points:

            if not point.locked:
                point.pos += self.camera_pos
                point.prevpos += self.camera_pos
                pos_before = point.pos.copy()
                point.pos += point.pos - point.prevpos
                if not self.frozen:
                    point.pos += np.array([0, 1])
                point.prevpos = pos_before.copy()
            else:
                point.pos += self.camera_pos

        if self.freeze_tick.tick() and not self.dont_freeze:
            self.frozen = True
            for point in self.points:
                point.prevpos = point.pos.copy()
            return
        else:
            r = 3





        for i in range(r):
            for stick in self.sticks:
                stick_centre = (stick.point1.pos + stick.point2.pos) / 2
                stick_dir = normalize(stick.point1.pos - stick.point2.pos)
                if not stick.point1.locked:
                    stick.point1.pos = stick_centre + stick_dir * stick.length / 2
                if not stick.point2.locked:
                    stick.point2.pos = stick_centre - stick_dir * stick.length / 2





class Point:
    def __init__(self, point, locked):
        self.pos = point
        self.prevpos = point
        self.locked = locked
        self.connecting = False
        self.render_light = False

    def render(self, screen):
        if self.locked:
            color = [255, 0, 0]
        else:
            color = [255, 255, 255]
        pygame.draw.circle(screen, color, self.pos, 10)

        if self.connecting:
            pygame.draw.line(
                screen, [255, 255, 255], self.pos, pygame.mouse.get_pos(), 4
            )


class Stick:
    def __init__(self, parent_cable, point1, point2, game):
        self.point1 = point1
        self.point2 = point2
        self.parent_cable = parent_cable
        self.length = np.linalg.norm(self.point1.pos - self.point2.pos)
        self.connected_sticks = []
        self.game_ref = game

        self.game_tick = self.game_ref.GT(30, oneshot = True)
        self.game_tick.value = self.game_tick.max_value
        self.i = 0
        self.start_object = None



    def render(self, screen, color):

        self.game_tick.tick()

        multiplier = (self.game_tick.max_value - self.game_tick.value) / self.game_tick.max_value

        if self.i == 3:
            if random.uniform(0,1) < 0.1:
                for i in range(2,4):
                    self.parent_cable.gen_spark(self.point1.pos + np.array(self.game_ref.camera_pos))
            self.game_tick.value = 0
            for x in (x for x in self.connected_sticks if x.i == 0):
                x.i = 4

            if self.start_object:
                for x in self.start_object.connected_cables:
                    if x == self or x.i != 0:
                        continue
                    x.i = 4

        if self.i > 0:
            self.i -= 1

        pygame.draw.line(screen, mult(color, multiplier) if color != [0,0,0] else [0,0,0], self.point1.pos, self.point2.pos, 4)

    def subdivide(self, points, sticks, lower_center):
        center = (self.point1.pos + self.point2.pos) / 2
        center_point = Point(
            np.array(center - np.array([0, lower_center]), dtype=np.float64), False
        )
        points.append(center_point)
        sticks.remove(self)
        sticks.append(Stick(self.parent_cable, self.point1, center_point, self.game_ref))
        sticks.append(Stick(self.parent_cable, self.point2, center_point, self.game_ref))


def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm
