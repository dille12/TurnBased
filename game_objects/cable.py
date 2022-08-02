from game_objects.game_object import Game_Object
import pygame
import numpy as np
from core.func import *


class Cable(Game_Object):
    def __init__(self, game, team, game_tick, start_obj = None, end_obj = None):
        self.points = []
        self.sticks = []
        self.game_tick = game_tick(30)
        self.team = team
        self.camera_pos = np.array([0,0])
        self.game_ref = game
        self.slot_size = [0,0]
        self.slot = [-1,-1]


    def tick(self):
        self.camera_pos = self.game_ref.delta
        self.Simulate()
        self.game_tick.tick()
        for x in self.sticks:
            x.render(self.game_ref.screen, color = mult(self.team, self.game_tick.value/self.game_tick.max_value))


    def generate(self, start, end, hanging, subdiv = 2):
        print("Starting generation")
        self.points.append(Point(np.array(start), True))
        self.startpoint = self.points[-1]
        self.points.append(Point(np.array(end), True))
        self.endpoint = self.points[-1]

        self.sticks.append(Stick(self.points[0], self.points[1]))



        for x in range(subdiv):
            sticks2 = self.sticks.copy()
            for stick in sticks2:
                stick.subdivide(self.points, self.sticks, lower_center = hanging)
                print("Subdivision complete")

        print("Cable generated")




    def Simulate(self):
        for point in self.points:

            if not point.locked:
                point.pos += self.camera_pos
                point.prevpos += self.camera_pos
                pos_before = point.pos.copy()
                point.pos += point.pos - point.prevpos

                point.pos += np.array([0,1])
                point.prevpos = pos_before.copy()
            else:
                point.pos += self.camera_pos

        for i in range(7):
            for stick in self.sticks:
                stick_centre = (stick.point1.pos + stick.point2.pos) / 2
                stick_dir = normalize(stick.point1.pos - stick.point2.pos)
                if not stick.point1.locked:
                    stick.point1.pos = stick_centre + stick_dir * stick.length/2
                if not stick.point2.locked:
                    stick.point2.pos = stick_centre - stick_dir * stick.length/2


class Point():
    def __init__(self,point, locked):
        self.pos = point
        self.prevpos = point
        self.locked = locked
        self.connecting = False

    def render(self, screen):
        if self.locked:
            color = [255,0,0]
        else:
            color = [255,255,255]
        pygame.draw.circle(screen, color, self.pos, 10)

        if self.connecting:
            pygame.draw.line(screen, [255,255,255], self.pos, pygame.mouse.get_pos(),4)


class Stick():
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2
        self.length = np.linalg.norm(self.point1.pos - self.point2.pos)


    def render(self, screen, color):
        pygame.draw.line(screen, color, self.point1.pos, self.point2.pos, 4)

    def subdivide(self, points, sticks, lower_center):
        center = (self.point1.pos + self.point2.pos) / 2
        center_point = Point(np.array(center - np.array([0,lower_center]), dtype=np.float64), False)
        points.append(center_point)
        sticks.remove(self)
        sticks.append(Stick(self.point1, center_point))
        sticks.append(Stick(self.point2, center_point))


def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
       return v
    return v / norm
