import pygame
from values import *
import core.func
import time
import math


class Game_Object:
    def __init__(self, game, team, name="obj", slot=None, hp = 100, size = [1,1]):
        self.name = name
        self.slot = slot
        self.game_ref = game
        self.size = [100*(size[0]), 100*(size[1])]
        self.slot_size = size

        self.active = False
        self.route_to_pos = [[0,0]]
        self.team = team
        self.hp = hp


    def slot_to_pos(self):
        return self.game_ref.get_pos([self.slot[0] * 100, self.slot[1] * 100])

    def scan_a_random_spot(self):
        free_spots = []
        end_points = self.scan_movement(2)
        for x in end_points:
            free_spots.append(x[-1])
        return free_spots



    def purchase(self, type):

        rand_spots = self.scan_a_random_spot()
        slot = core.func.pick_random_from_list(rand_spots)
        self.game_ref.gen_object(type, self.team, slot)



    def slot_to_pos_center(self):
        return [self.slot[0] * 100 + self.size[0]/2, self.slot[1] * 100 + self.size[1]/2]

    def slot_to_pos_c_cam(self):
        return self.game_ref.get_pos([self.slot[0] * 100 + self.size[0]/2, self.slot[1] * 100 + self.size[1]/2])


    def slot_to_pos_c(self, slot):
        return self.game_ref.get_pos([slot[0] * 100, slot[1] * 100])

    def render(self):
        x, y = self.slot_to_pos()
        if self.active:
            pygame.draw.rect(self.game_ref.screen, self.team, [x+5, y+5, self.size[0]-10, self.size[1]-10], 4)
            core.func.render_text(self.game_ref, self.name, [x+self.size[0]/2, y-20], 20, centerx = True, color = self.team)
            core.func.render_text(self.game_ref, f"HP:{self.hp}", [x+self.size[0]/2, y+self.size[1]+20], 20, centerx = True, color = self.team)
        else:
            pygame.draw.rect(self.game_ref.screen, self.team, [x+5, y+5, self.size[0]-10, self.size[1]-10], 1)
        if self.image != None:
            self.game_ref.screen.blit(self.image, [x,y])


    def rotate(self, target):

        angle = math.degrees(math.atan2(self.pos, target))
        image_rot, rect = core.func.rot_center(self.image, angle, 0,0)






    def click(self):
        x,y = self.slot_to_pos()

        if x < self.game_ref.mouse_pos[0] < x + self.size[0] and y < self.game_ref.mouse_pos[1] < y + self.size[1] and "mouse0" in self.game_ref.keypress:
            print("CLICKED")
            self.game_ref.sounds["select1"].play()
            if not self.active:
                self.activate()
                self.deactivate_other()
            else:
                self.activate(False)
                self.routes = []

    def deactivate_other(self):
        for x in self.game_ref.render_layers.keys():
            for obj in self.game_ref.render_layers[x]:
                if obj != self:
                    obj.activate(False)


    def activate(self, boolean = True):
        if not boolean:
            if self.game_ref.activated_object == self:
                self.game_ref.activated_object = None
        else:
            self.center()
            self.game_ref.activated_object = self
        self.active = boolean


    def render_routes(self):
        rendered = [0,0,0,0,0,0,0,0]
        if self.route_to_pos == []:
            self.route_to_pos = [0,0]
        for route in self.routes:
            for slot in route:
                if slot in rendered:
                    continue
                rendered.append(slot)

                x,y = self.slot_to_pos_c(slot)
                if core.func.point_inside(self.game_ref.mouse_pos, [x+10,y+10], [80,80]):

                    if self.slot != slot:

                        pygame.draw.rect(self.game_ref.screen, core.func.mult(self.team, 0.8), [x+10, y+10, 80,80],10)

                        if self.route_to_pos[-1] != slot:
                            self.route_to_pos = core.func.get_shortest_route(slot, self.routes)
                            print("Calculated new")

                        last_x_y = core.func.minus(self.slot.copy(),[0.5, 0.5])

                        for pos in self.route_to_pos:
                            pos = core.func.minus(pos.copy(),[0.5, 0.5])
                            pygame.draw.line(self.game_ref.screen, self.team, self.slot_to_pos_c(last_x_y), self.slot_to_pos_c(pos),4)
                            last_x_y = pos.copy()

                        if "mouse0" in self.game_ref.keypress:
                            print(self.route_to_pos)
                            self.moving_route = self.route_to_pos
                            self.activate(False)
                            self.move_tick.value = self.move_tick.max_value



                elif self.slot != slot:

                    pygame.draw.rect(self.game_ref.screen, core.func.mult(self.team, 0.5), [x+10, y+10, 80,80],5)


    def center(self):
        self.game_ref.camera_pos_target = core.func.minus(self.slot_to_pos_center(),core.func.mult(self.game_ref.resolution,0.5), op="-")

    def tick_buttons(self):
        if self.active:
            for x in self.buttons:
                x.tick()


    def scan_movement(self, movement_range):
        if movement_range == 0:
            return []
        occ_slots = self.game_ref.get_occupied_slots()
        open_routes = [[self.slot.copy()]]
        finished_routes = []
        t = time.time()
        while open_routes != []:
            route = open_routes[0]
            open_routes.remove(route)
            tile = route[-1]
            open_tiles = self.scan_tile(tile,occ_slots)
            for x in open_tiles:
                if len(route) == movement_range:
                    finished_routes.append(route + [[x[0],x[1]]])
                else:
                    open_routes.append(route + [[x[0],x[1]]])
        print("Finished")
        print(time.time()-t)
        return finished_routes






    def scan_tile(self, tile, occ_slots):
        open_routes = []
        for x, y in [[1,0], [0,1], [-1,0], [0,-1]]:
            tile2 = core.func.minus(tile.copy(),[x,y])
            if tile2 not in occ_slots and 0 <= tile2[0] < 25 and 0 <= tile2[1] < 25:
                open_routes.append(tile2)

        return open_routes
