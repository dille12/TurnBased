import pygame
from values import *
import core.func
import time
import math
import random
import numpy as np
from game_objects.particles.spark import Spark
from game_objects.particles.ash import Ash
from game_objects.particles.explosion_particles import ExplosionParticle
import core.path_finding
from _thread import *
from game_objects.object_render import render

from game_objects.abilities.get_abilities import *
from hud_elements.unit_status import UnitStatus



class Game_Object:
    def __init__(self, game, team, name="obj", slot=None, hp=100, size=[1, 1]):
        self.name = name
        self.slot = slot
        self.game_ref = game
        self.size = [100 * (size[0]), 100 * (size[1])]
        self.slot_size = size

        get_abilities(self)

        self.id = random.randint(0, 2**16)

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
        self.finding_route = False
        self.disabled_for_turns = 0
        self.unitstatuses = []

        self.shots_per_round = 1
        self.shots = 1
        self.act_gt = self.game_ref.GT(20, oneshot=True)
        self.requirement = None
        self.render = render

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
        for x_s in range(object.slot_size[0]):
            for y_s in range(object.slot_size[1]):
                if abs(self.slot[0] - object.slot[0] + x_s) <= self.range and abs(self.slot[1] - object.slot[1] + y_s) <= self.range:
                    return True
        return False

    def enemy_check(self, object, dict, dict2):
        for x in dict:
            if object.__dict__[x] != dict[x]:
                return False
        for x in dict2:
            if object.__dict__[x] == dict2[x]:
                return False
        return True



    def scan_enemies(self, include = {}, exclude = {}):
        self.shootables = []
        for x in (
            x
            for x in self.game_ref.return_objects(["3.BUILDINGS", "4.NPCS"])
            if x.team != BLACK and self.in_range(x) #x.team != self.team and
        ):
            if self.enemy_check(x, include, exclude):
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
        self.game_ref.datagatherer.data.append(
            f"self.game_ref.find_object_id({id}).{exec}"
        )

    def send_info(self, list, id_override=False):

        if id_override:
            obj = self.game_ref.find_object_id(id_override)
        else:
            obj = self

        info = obj.get_dict(list)

        self.game_ref.datagatherer.data.append(
            f"self.game_ref.find_object_id({obj.id}).set_dict({info})"
        )

    def center_slot(self):
        return [self.slot[0] + self.slot_size[0]/2, self.slot[1] + self.slot_size[1]/2]

    def hp_change(self, amount):

        UnitStatus(self, f"{amount}HP!",20, [255,0,0])

        self.hp += amount
        if self.hp <= 0:
            self.kill()

    def tick_statuses(self):
        for x in self.unitstatuses:
            x.tick()

    def tick_action(self, outcome, text = "SHOOT", argument = 0):
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
                    f"R-CLICK: {text}",
                    core.func.minus(self.game_ref.mouse_pos, [0, -100]),
                    30,
                    centerx=True,
                    color=[255, 0, 0],
                )

                if "mouse2" in self.game_ref.keypress:

                    method = [method_name for method_name in dir(self) if outcome == getattr(self, method_name)][0]

                    self.game_ref.datagatherer.data.append(
                    f"self.game_ref.find_object_id({self.id}).{method}(self.game_ref.find_object_id({self.id}), self.game_ref.find_object_id({obj.id}), argument = {argument})"
                    )

                    outcome(self, obj, argument)


    def connected_building(self):
        return (self.connected_to_base or self.name == "Base") and self.disabled_for_turns == 0



    def create_spark(self, force = False):
        if (random.uniform(0, 1) > 0.04 or (not self.connected_building() or self.type == "npc")) or force:
            return
        token = random.randint(0, 1)
        if token:
            x = random.uniform(
                self.slot[0] * 100, (self.slot[0] + self.slot_size[0]) * 100
            )
            y = self.slot[1] * 100 + random.randint(0, 1) * self.slot_size[1] * 100
        else:
            x = self.slot[0] * 100 + random.randint(0, 1) * self.slot_size[0] * 100
            y = random.uniform(
                self.slot[1] * 100, (self.slot[1] + self.slot_size[1]) * 100
            )
        self.gen_spark([x, y])

    def gen_spark(self, point):
        self.game_ref.render_layers["PARTICLES"].append(
            Spark(self.game_ref, point, [random.uniform(-3, 3), random.uniform(-3, 3)])
        )

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

    def delete(self):
        if "del" in self.game_ref.keypress and self.active:
            self.kill()

            self.game_ref.scan_connecting_cables()
            self.game_ref.datagatherer.data.append(
                f"self.game_ref.find_object_id({self.id}).kill()"
            )

    def own(self):
        return self.team == self.game_ref.player_team

    def kill(self):

        x, y = self.slot_to_pos_center()
        print(x, y)

        if self.game_ref.activated_object == self:
            self.game_ref.activated_object = None

        for i in range(16):
            self.game_ref.render_layers["PARTICLES"].append(Ash(self.game_ref, [x, y]))
        for i in range(80):
            self.game_ref.render_layers["PARTICLES"].append(
                ExplosionParticle(self.game_ref, [x, y])
            )

        self.game_ref.vibration = 35

        max_dist = 5000

        core.func.pick_random_from_list([self.game_ref.sounds["death1"], self.game_ref.sounds["death2"], self.game_ref.sounds["death3"]]).play()
        if self.own():
            self.game_ref.chat.append(f"{self.name} has been destroyed.")

        for x1 in self.game_ref.return_objects():
            if self.type == "building":
                if x1.type != "cable":
                    continue
                if x1.start_obj == self or x1.end_obj == self:
                    self.game_ref.render_layers["5.CABLE"].remove(x1)
                    print("Killing", x1)

        for cable1 in self.game_ref.return_objects(["5.CABLE"]):
            for point in cable1.points:
                if not point.locked:
                    dist = core.func.get_dist_points([x,y], point.pos)
                    if dist < max_dist:
                        cable1.frozen = False
                        cable1.freeze_tick.value = 0
                        angle = core.func.get_angle([x,y], point.pos, radians = True)
                        nudge = np.array([math.cos(angle) * (max_dist-dist)/100, math.sin(angle) * (max_dist-dist)/100])
                        point.pos += nudge


        self.game_ref.scan_connecting_cables()

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

    def check_slot_los(self, x,y):
        if not self.game_ref.draw_los:
            return True
        pxarray = pygame.PixelArray(self.game_ref.los_image)
        for x1 in range(2):
            for y1 in range(2):
                try:
                    if pxarray[int(round(x + x1*100)), int(round(y + y1*100))] != 0:
                        return True
                except:
                    pass
        return False

    def check_los(self):
        if not self.game_ref.draw_los:
            return True
        x, y = self.slot_to_pos_center()
        pxarray = pygame.PixelArray(self.game_ref.los_image)
        try:
            if pxarray[int(x), int(y)] == 0:
                return False
        except:
            return False
        return True

    def slot_to_pos_c(self, slot, center = False, no_cam = False):
        c = 0
        if center:
            c = self.size[0] / 2
        return self.game_ref.get_pos([slot[0] * 100+c, slot[1] * 100+c]) if not no_cam else [slot[0] * 100+c, slot[1] * 100+c]



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
            for obj in self.game_ref.return_objects(["3.BUILDINGS", "4.NPCS"]):
                if obj != self:
                    obj.activate(False)

    def activate(self, boolean=True):
        if not boolean:
            self.render_long_routes = False
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

            self.game_ref.activated_object = self
        self.active = boolean

    def render_long_range(self):
        target = self.pos_to_slot(self.game_ref.get_pos_rev(self.game_ref.mouse_pos))
        x,y = self.slot_to_pos_c(target, center = False, no_cam = True)
        x1,y1 = self.slot_to_pos_c(target, center = False, no_cam = False)
        non_reachable = False
        if self.route_to_pos != []:
            if self.route_to_pos[-1] != target:
                non_reachable = True
        if not self.check_slot_los(x,y) or target in self.game_ref.get_occupied_slots():
            non_reachable = True

        if non_reachable:
            self.route_to_pos = []
            self.target_pos = [-1,-1]
            pygame.draw.rect(
                self.game_ref.screen,
                [255,0,0],
                [x1 + 10, y1 + 10, 80, 80],
                3,
            )
            return

        pygame.draw.rect(
            self.game_ref.screen,
            core.func.mult(self.team.color, 0.8),
            [x1 + 10, y1 + 10, 80, 80],
            5,
        )



        if self.target_pos != target:

            if not self.finding_route:
                print("Computing new route")
                start_new_thread(core.path_finding.compute, (self, self.slot, target, self.game_ref.get_occupied_slots(), self.game_ref.size_slots))

        if self.route_to_pos != []:
            self.render_lines_route()

    def render_lines_route(self, route = False):
        if not route:
            route = self.route_to_pos
        last_x_y = core.func.minus(self.slot.copy(), [0.5, 0.5])
        color = self.team.color.copy()
        turn = 0
        for i, pos in enumerate(route[:self.battery_life+1]):
            turn_indicator = False
            if i == self.turn_movement+1 or (i > self.turn_movement and (i-1)%self.movement_range == 0):

                color = core.func.mult(color,0.8)
                turn += 1
                turn_indicator = True

            x3, y3 = self.slot_to_pos_c(pos)

            pygame.draw.rect(
                self.game_ref.screen,
                color if i+1 != len(route) else [255,255,255],
                [x3+5,y3+5,90,90],
                1 if i+1 != len(route) else 3
            )

            pos = core.func.minus(pos.copy(), [0.5, 0.5])

            x1, y1 = self.slot_to_pos_c(last_x_y)
            x2, y2 = self.slot_to_pos_c(pos)

            origin = [min([x1,x2])-5, min([y1,y2])-5]

            surf = pygame.Surface([abs(x1-x2)+10, abs(y1-y2)+10], pygame.SRCALPHA, 32).convert_alpha()



            pygame.draw.line(
                surf,
                color,
                [x1-origin[0]+5, y1-origin[1]+5],
                [x2-origin[0]+5, y2-origin[1]+5],
                7,
            )

            core.func.blit_glitch(self.game_ref, surf, origin, glitch = 10, diagonal = True)

            if turn_indicator:
                core.func.render_text_glitch(self.game_ref, str(turn), self.slot_to_pos_c(last_x_y), 30, color = [255,255,255], glitch = 1)
            last_x_y = pos.copy()

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

                        self.render_lines_route()

                        if (
                            "mouse2" in self.game_ref.keypress_held_down
                            and self.game_ref.own_turn
                        ):
                            self.moving_route = self.route_to_pos[:self.battery_life+1]
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

    def get_circuit_breaker(self):
        if self.name == "Electric Tower" or self.name == "Base":
            if self.short_circuited:
                return True
        return False

    def toggle_circuits(self, boolean):

        self.short_circuited = boolean

        if boolean:
            self.energy_consumption = 3
        else:
            self.energy_consumption = 0

        self.send_info(["short_circuited"])

    def short_circuit_recovery(self):
        if self.disabled_for_turns > 0:
            self.disabled_for_turns -= 1



    def tick_buttons(self):
        if self.active:
            for x in self.buttons:
                x.tick()

    def los(self):

        if not self.game_ref.draw_los:
            return

        if self.team == self.game_ref.player_team:

            if self.type == "building":
                if not self.connected_building():
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
