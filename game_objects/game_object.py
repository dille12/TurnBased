import pygame
from values import *
import core.func
import time
import math
import random

from game_objects.particles.spark import Spark


class Game_Object:
    def __init__(self, game, team, name="obj", slot=None, hp=100, size=[1, 1]):
        self.name = name
        self.slot = slot
        self.game_ref = game
        self.size = [100 * (size[0]), 100 * (size[1])]
        self.slot_size = size

        self.id = random.randint(0,2**16)

        self.classname = self.name.replace(" ", "")
        self.active = False
        self.route_to_pos = [[0, 0]]
        self.team = team
        self.hp_max = hp
        self.hp = hp
        self.buttons = []
        self.mode = ""
        self.build_queue = []
        self.c_build_time = 0
        self.connected_to_base = False
        self.los_rad = 250

        self.shots_per_round = 1
        self.shots = 1
        self.act_gt = self.game_ref.GT(20, oneshot=True)

    def __str__(self):
        return f"{self.classname} {self.team.name} {self.slot} {self.id}"

    def slot_to_pos(self):
        return self.game_ref.get_pos([self.slot[0] * 100, self.slot[1] * 100])

    def pos_to_slot(self, pos):
        return [round(pos[0] / 100 - 0.5), round(pos[1] / 100 - 0.5)]

    def check_mode(self):
        for x in self.buttons:
            if x.active and x.activator != "":
                self.mode = x.activator
                if self.mode == "walk":
                    self.routes = self.scan_movement(self.turn_movement)
                return

    def scan_a_random_spot(self):
        free_spots = []
        end_points = self.scan_movement(2)
        for x in end_points:
            free_spots.append(x[-1])
        return free_spots

    def in_range(self, object):
        return (
            abs(self.slot[0] - object.slot[0]) <= self.range
            and abs(self.slot[1] - object.slot[1]) <= self.range
        )

    def scan_enemies(self):
        self.shootables = []
        for x in (
            x
            for x in self.game_ref.return_objects(["3.BUILDINGS", "4.NPCS"])
            if x.team != self.team and x.team != BLACK and self.in_range(x)
        ):
            self.shootables.append(x)


    def set_dict(self, list):
        for x in list:
            self.__dict__[x] = list[x]

    def get_dict(self, list):
        list2 = {}
        for x in list:
            list2[x] = self.__dict__[x]
        return list2

    def exec_on_obj(self, id, exec):
        self.game_ref.datagatherer.data.append(f"self.game_ref.find_object_id({id}).{exec}")


    def send_info(self, list, id_override = False):

        if id_override:
            obj = self.game_ref.find_object_id(id_override)
        else:
            obj = self

        info = obj.get_dict(list)

        self.game_ref.datagatherer.data.append(f"self.game_ref.find_object_id({obj.id}).set_dict({info})")


    def center_slot(self):
        return [self.slot[0] + self.slot_size[0], self.slot[1] + self.slot_size[1]]

    def hp_change(self, amount):
        self.hp += amount
        if self.hp <= 0:
            self.kill()

    def highlight_enemies(self):
        for obj in self.shootables:
            x, y = obj.slot_to_pos()
            pygame.draw.rect(
                self.game_ref.screen, [255, 0, 0], [x, y, obj.size[0], obj.size[1]], 7
            )

            if core.func.point_inside(self.game_ref.mouse_pos, [x, y], obj.size):

                pygame.draw.line(
                    self.game_ref.screen,
                    [255, 0, 0],
                    self.slot_to_pos_c_cam(),
                    obj.slot_to_pos_c_cam(),
                    6,
                )

                core.func.render_text(
                    self.game_ref,
                    "SHOOT R-CLICK",
                    core.func.minus(self.game_ref.mouse_pos, [0, -100]),
                    30,
                    centerx=True,
                    color=[255, 0, 0],
                )

                if "mouse2" in self.game_ref.keypress:
                    self.shots -= 1
                    obj.hp_change(-50)

                    self.exec_on_obj(obj.id, "hp_change(-50)")

    def connected_building(self):
        return self.connected_to_base or self.name == "Base"

    def create_spark(self):
        if random.uniform(0,1) > 0.04 or not self.connected_building():
            return
        token = random.randint(0,1)
        if token:
            x = random.uniform(self.slot[0]*100, (self.slot[0] + self.slot_size[0])*100)
            y = self.slot[1]*100 + random.randint(0,1) * self.slot_size[1]*100
        else:
            x = self.slot[0]*100 + random.randint(0,1) * self.slot_size[0]*100
            y = random.uniform(self.slot[1]*100, (self.slot[1] + self.slot_size[1])*100)
        self.game_ref.render_layers["PARTICLES"].append(Spark(self.game_ref, [x,y],[random.uniform(-3,3), random.uniform(-3,3)]))



    def tick_queue(self):

        if self.build_queue != [] and self.c_build_time == 0:

            self.generate(self.build_queue[0])
            self.build_queue.remove(self.build_queue[0])
            if self.build_queue != []:
                self.c_build_time = self.build_queue[0].buildtime

        if self.build_queue != [] and self.active:
            core.func.render_text(
                self.game_ref, "QUEUE:", [50, 870], 20, color=self.team.color
            )
            x_pos = -50
            i = 0
            for x in self.build_queue:
                x_pos += 100
                self.game_ref.screen.blit(
                    x.image if i == 0 else x.image_bg, [x_pos, 900]
                )

                i += 1
            pygame.draw.rect(
                self.game_ref.screen, self.team.color, [50, 900, 100, 100], 2
            )
            core.func.render_text(
                self.game_ref, self.c_build_time, [55, 905], 50, color=self.team.color
            )

    def purchase(self, type):
        if (
            type.energy_consumption + self.team.energy_consumption
            <= self.team.energy_generation
        ):
            if len(self.build_queue) < 10:
                self.build_queue.append(type)
                if len(self.build_queue) == 1:
                    self.c_build_time = type.buildtime

    def generate(self, type):
        rand_spots = self.scan_a_random_spot()
        slot = core.func.pick_random_from_list(rand_spots)
        type.slot = slot
        self.game_ref.gen_object(type)

    def kill(self):
        for x in self.game_ref.render_layers.keys():
            for obj in self.game_ref.render_layers[x]:
                if obj == self:
                    self.game_ref.render_layers[x].remove(self)

    def slot_to_pos_center(self):
        return [
            self.slot[0] * 100 + self.size[0] / 2,
            self.slot[1] * 100 + self.size[1] / 2,
        ]

    def slot_to_pos_c_cam(self):
        return self.game_ref.get_pos(
            [
                self.slot[0] * 100 + self.size[0] / 2,
                self.slot[1] * 100 + self.size[1] / 2,
            ]
        )

    def check_los(self):
        x, y = self.slot_to_pos_center()
        pxarray = pygame.PixelArray(self.game_ref.los_image)
        if pxarray[int(x), int(y)] == 0:
            return False
        return True

    def slot_to_pos_c(self, slot):
        return self.game_ref.get_pos([slot[0] * 100, slot[1] * 100])

    def render(self):
        if self.type == "wall":
            return
        if not self.check_los():
            return

        x, y = self.slot_to_pos()

        if self.active:

            smooth_lines_x = self.smoothing_inv * self.slot_size[0] / (3)
            smooth_lines_y = self.smoothing_inv * self.slot_size[1] / (3)

            lines_pos = (1 - self.smooth_value_raw) * 50 + 2

            pygame.draw.line(
                self.game_ref.screen,
                [255, 255, 255],
                [x - lines_pos, y - lines_pos],
                [x - lines_pos + smooth_lines_x, y - lines_pos],
                2,
            )
            pygame.draw.line(
                self.game_ref.screen,
                [255, 255, 255],
                [x - lines_pos, y - lines_pos],
                [x - lines_pos, y - lines_pos + smooth_lines_y],
                2,
            )

            pygame.draw.line(
                self.game_ref.screen,
                [255, 255, 255],
                [
                    x + lines_pos + self.size[0] - smooth_lines_x,
                    y + lines_pos + self.size[1],
                ],
                [x + lines_pos + self.size[0], y + lines_pos + self.size[1]],
                2,
            )
            pygame.draw.line(
                self.game_ref.screen,
                [255, 255, 255],
                [
                    x + lines_pos + self.size[0],
                    y + lines_pos + self.size[1] - smooth_lines_y,
                ],
                [x + lines_pos + self.size[0], y + lines_pos + self.size[1]],
                2,
            )

            pygame.draw.rect(
                self.game_ref.screen,
                self.team.color,
                [x + 5, y + 5, self.size[0] - 10, self.size[1] - 10],
                4,
            )
            core.func.render_text(
                self.game_ref,
                self.name,
                [x + self.size[0] / 2, y - 15],
                20,
                centerx=True,
                color=self.team.color,
            )
            core.func.render_text(
                self.game_ref,
                f"HP:{self.hp}",
                [x + self.size[0] / 2, y + self.size[1] + 20],
                20,
                centerx=True,
                color=self.team.color,
            )
        else:
            pygame.draw.rect(
                self.game_ref.screen,
                self.team.color,
                [x + 5, y + 5, self.size[0] - 10, self.size[1] - 10],
                1,
            )
        if self.image != None:
            self.game_ref.screen.blit(self.image, [x, y])

        if hasattr(self, "turn_movement"):
            for x_1 in range(self.turn_movement):
                pygame.draw.rect(
                    self.game_ref.screen,
                    self.team.color,
                    [
                        x + 5 + 92,
                        y + 5 + x_1 * round(93 / self.movement_range),
                        6,
                        round(93 / self.movement_range) - 10
                    ],
                )

                pygame.draw.rect(
                    self.game_ref.screen,
                    core.func.mult(self.team.color, 0.5),
                    [
                        x + 5 + 92,
                        y + 5 + x_1 * round(93 / self.movement_range),
                        6,
                        round(93 / self.movement_range) - 10
                    ],
                    1
                )

        if self.team != nature:
            pygame.draw.rect(
                self.game_ref.screen,
                self.team.color,
                [
                    x + 5,
                    y + 5 + self.size[1],
                    round(self.size[0]*0.95 * self.hp/self.hp_max),
                    6
                ]
            )

            pygame.draw.rect(
                self.game_ref.screen,
                core.func.mult(self.team.color, 0.5),
                [
                    x + 3,
                    y + 3 + self.size[1],
                    round(self.size[0] * 0.95)+4,
                    10
                ],
                1
            )

    def rotate(self, target):

        angle = math.degrees(math.atan2(self.pos, target))
        image_rot, rect = core.func.rot_center(self.image, angle, 0, 0)


    def gen_string(self):

        return f"{self.classname}(self.game_ref, {self.team.str_team}, {self.slot})"


    def click(self):

        if not self.check_los():
            return



        x, y = self.slot_to_pos()

        if (
            x < self.game_ref.mouse_pos[0] < x + self.size[0]
            and y < self.game_ref.mouse_pos[1] < y + self.size[1]
            and "mouse0" in self.game_ref.keypress
        ):
            print("CLICKED")

            if self.team != self.game_ref.player_team:
                print(self.game_ref.player_team.__dict__)
                print(self.team.__dict__)
                return

            if not self.active:
                self.activate()
                self.deactivate_other()
            else:
                self.activate(False)
                self.routes = []

    def deactivate_other(self):
        print("Deactivating other from", self)
        for x in self.game_ref.render_layers.keys():
            for obj in self.game_ref.return_objects(["3.BUILDINGS","4.NPCS"]):
                if obj != self:
                    obj.activate(False)

    def activate(self, boolean=True):
        if not boolean:

            self.build = None
            if self.game_ref.activated_object == self:
                self.game_ref.activated_object = None
        else:
            print("Activating", self)
            self.act_gt.value = 0
            self.game_ref.activated_a_object = True
            self.center()

            self.select_sound.stop()
            self.select_sound.play()
            if self.range != 0:
                self.scan_enemies()
            self.game_ref.activated_object = self
        self.active = boolean

    def render_routes(self):
        rendered = [0, 0, 0, 0, 0, 0, 0, 0]
        if self.route_to_pos == []:
            self.route_to_pos = [0, 0]
        for route in self.routes:
            for slot in route:
                if slot in rendered:
                    continue
                rendered.append(slot)

                x, y = self.slot_to_pos_c(slot)
                if core.func.point_inside(
                    self.game_ref.mouse_pos, [x + 10, y + 10], [80, 80]
                ):

                    if self.slot != slot:

                        pygame.draw.rect(
                            self.game_ref.screen,
                            core.func.mult(self.team.color, 0.8),
                            [x + 10, y + 10, 80, 80],
                            10,
                        )

                        if self.route_to_pos[-1] != slot:
                            self.route_to_pos = core.func.get_shortest_route(
                                slot, self.routes
                            )

                        last_x_y = core.func.minus(self.slot.copy(), [0.5, 0.5])

                        for pos in self.route_to_pos:
                            pos = core.func.minus(pos.copy(), [0.5, 0.5])
                            pygame.draw.line(
                                self.game_ref.screen,
                                self.team.color,
                                self.slot_to_pos_c(last_x_y),
                                self.slot_to_pos_c(pos),
                                4,
                            )
                            last_x_y = pos.copy()

                        if "mouse2" in self.game_ref.keypress and self.game_ref.own_turn:
                            self.moving_route = self.route_to_pos
                            self.activate(False)
                            self.move_tick.value = self.move_tick.max_value
                            self.send_info(["moving_route"])

                elif self.slot != slot:

                    pygame.draw.rect(
                        self.game_ref.screen,
                        core.func.mult(self.team.color, random.uniform(0.45, 0.55)),
                        [
                            x + 10 + random.randint(-1, 1),
                            y + 10 + random.randint(-1, 1),
                            80,
                            80,
                        ],
                        5,
                    )

    def center(self):
        self.game_ref.camera_pos_target = core.func.minus(
            self.slot_to_pos_center(),
            core.func.mult(self.game_ref.resolution, 0.5),
            op="-",
        )

    def tick_buttons(self):
        if self.active:
            for x in self.buttons:
                x.tick()

    def los(self):
        if self.team == self.game_ref.player_team:

            if self.type == "building":
                if not self.connected_to_base and not self.name == "Base":
                    return

            pygame.draw.circle(
                self.game_ref.los_image,
                [255, 255, 255],
                self.slot_to_pos_center(),
                self.los_rad,
            )

    def activation_smoothing(self):
        self.act_gt.tick()
        value = min([self.act_gt.value / self.act_gt.max_value, 1])
        self.smoothing = (1 - value) ** 3.5 * 150
        self.smoothing_inv = (value) ** 3.5 * 150
        self.smooth_value = (1 - value) ** 3.5
        self.smooth_value_raw = value

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
            open_tiles = self.scan_tile(tile, occ_slots)
            for x in open_tiles:
                if len(route) == movement_range:
                    finished_routes.append(route + [[x[0], x[1]]])
                else:
                    open_routes.append(route + [[x[0], x[1]]])
        print("Finished")
        print(time.time() - t)
        return finished_routes

    def scan_tile(self, tile, occ_slots):
        open_routes = []
        for x, y in [
            [1, 0],
            [0, 1],
            [-1, 0],
            [0, -1],
            [1, 1],
            [1, -1],
            [-1, -1],
            [-1, 1],
        ]:
            tile2 = core.func.minus(tile.copy(), [x, y])
            if tile2 not in occ_slots and 0 <= tile2[0] < 25 and 0 <= tile2[1] < 25:
                open_routes.append(tile2)

        return open_routes
