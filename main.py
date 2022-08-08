import pygame
from texture.texture import load_images
from sounds.sounds import load_sounds
from game_objects.game_object import *
from game_objects.npc import *
from game_objects.building import *
from game_objects.wall import *
from game_objects.deposit import *
from values import *
import sys
from core.keypress import *
from core.camera_movement import *
from core.image_transform import *
from core.func import *
from core.map_gen import *
import numpy as np
from game_objects.objects import *
from core.player import Player
from hud_elements.button import *
import gamestates.battle
import gamestates.menu
import socket
from networking.datagatherer import DataGatherer


class Game:

    """
    Game class to contain all information for ease of access.
    """

    def __init__(self, resolution):
        pygame.init()
        pygame.font.init()

        self.GT = GameTick

        self.datagatherer = DataGatherer(self)

        self.resolution = resolution

        self.generation_overflow_tick = self.GT(30)

        hostname = socket.gethostname()
        self.own_ip = socket.gethostbyname(hostname)

        self.images = {}
        self.sounds = {}
        self.terminal = {}
        self.size_conv = [1920 / resolution[0], 1080 / resolution[1]]

        self.surf = pygame.Surface((300, 100))
        self.surf.set_alpha(100)
        self.surf.fill((0, 0, 0))

        self.camera_pos = [0, 0]
        self.prev_pos = [0, 0]
        self.camera_pos_target = [0, 0]
        self.error_message = None
        self.player_team = placeholder
        self.connected_players = []
        self.notification_tick = self.GT(180, oneshot = True)
        self.notification = ""
        self.notification_color = [255,255,255]

        self.qsc = 1920 / resolution[0]

        self.ss = 100 * self.qsc  # SLOT SIZE
        self.smoothing = 0

        self.screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
        load_images(self, self.size_conv)
        load_sounds(self)



        self.state = gamestates.menu.Menu(self)



        print(self.images)
        print(self.sounds)

        self.clock = pygame.time.Clock()
        self.map_size = self.images["map"].get_size()
        self.los_image = pygame.Surface(self.images["map"].get_size()).convert()
        self.los_image.fill([0, 0, 0])
        # self.los_image.set_alpha(100)
        self.los_image.set_colorkey([255, 255, 255])

        self.size_slots, tiles, self.deposits = gen_map(self.images["layout"])

        self.render_layers = {
            "1.BOTTOM": [],
            "2.ORE": [],
            "3.BUILDINGS": [],
            "4.NPCS": [],
            "5.CABLE": [],
            "6.HUD": [],
        }
        #self.render_layers["3.BUILDINGS"].append(Building(self,green_t,"Base",[3,3], image = self.images["base"].copy(), size = [2,2]))
        #self.render_layers["3.BUILDINGS"].append(Base(self, blue_t, [1,1]))
        # self.render_layers["3.BUILDINGS"].append(Base(self, red_t, [22,22]))
        #
        # self.render_layers["4.NPCS"].append(Builder(self, blue_t, [3,2]))

        for x in self.deposits:
            self.render_layers["1.BOTTOM"].append(Deposit(self, nature, "Wall", x))

        for x in tiles:
            self.render_layers["1.BOTTOM"].append(Wall(self, nature, "Wall", x))

        self.next_turn_button = Button(
            self,
            self,
            17,
            8.5,
            self.player_team.color,
            self.images["nextturn"],
            oneshot=True,
            oneshot_func=self.end_turn,
        )
        self.own_turn = True
        self.keypress = []
        self.keypress_held_down = []
        self.cam_moving = False
        self.timedelta = 1
        self.activated_object = None
        self.fps = 0
        self.idle = 0

    def get_pos(self, pos):
        # return minus(pos,self.camera_pos, op = "-")
        return minus(minus(pos, self.camera_pos, op="-"), self.size_conv, op="/")

    def get_pos_rev(self, pos):
        return minus(minus(pos, self.camera_pos, op="+"), self.size_conv, op="/")

    def set_notification(self, text, color = [255,255,255]):
        self.notification_color = color
        self.notification = text
        self.notification_tick.value = 0

    def begin_turn(self):
        for x in self.return_objects():

            if hasattr(x, "turn_movement"):
                x.turn_movement = x.movement_range
            if hasattr(x, "shots"):
                x.shots = x.shots_per_round
            if hasattr(x, "c_build_time"):
                if x.c_build_time > 0:
                    x.c_build_time -= 1

    def end_turn(self, arg):

        self.los_image.fill([0, 0, 0])
        for x in self.return_objects():
            if x.type == "building":
                x.los()


        for i, x in enumerate(self.connected_players):
            if x == self.player_team:

                if i == len(self.connected_players) - 1:
                    next_player = self.connected_players[0]
                else:
                    next_player = self.connected_players[i+1]


                self.set_turn(next_player.str_team, send_info = True)
                print("Next turn is", next_player)

                return

    def set_turn(self, player, send_info = False):
        for x in self.connected_players:
            if x.str_team == player:
                self.turn = x

                if send_info:
                    self.datagatherer.data.append(f"self.game_ref.set_turn(\"{x.str_team}\")")

                if self.player_team.str_team == x.str_team:
                    print("own turn")
                    self.begin_turn()
                self.sounds["turn_change"].stop()
                self.sounds["turn_change"].play()
                self.set_notification(f"{x.name}'s turn", color = x.color)

                return

    def tick_alert(self):
        if not self.notification_tick.tick() and self.notification_tick.value > 20:
            tick = self.notification_tick.value - 20
            alpha = 255
            if tick < 40:
                alpha = 255 * tick/40

            elif 160 > tick > 100:
                alpha = 255 * (160 - tick)/60

            text = self.terminal[60].render(self.notification, False, self.notification_color)
            text.set_alpha(alpha)
            self.screen.blit(text, [self.resolution[0]/2 - text.get_rect().center[0], self.resolution[1]/3 - text.get_rect().center[1]])




    def slot_inside(self, slot):
        return 0 <= slot[0] < self.size_slots[0] and 0 <= slot[1] < self.size_slots[1]

    def scan_connecting_cables(self):
        print("Scanning cablenetwork")
        self.connected_in_scan = 0
        for x in self.render_layers["3.BUILDINGS"]:
            if x.name == "Base" and x.team == self.player_team:
                print(x)
                base = x
                break

        for cable in self.render_layers["5.CABLE"]:
            cable.disconnect()

        while 1:
            connected_last = self.connected_in_scan
            for cable in self.render_layers["5.CABLE"]:
                print(cable.start_obj, cable.end_obj)
                if base in [cable.start_obj, cable.end_obj]:
                    print("BASE FOUND")
                    cable.connect()
                cable.update()
            print("CONNECTED:", self.connected_in_scan)
            if connected_last == self.connected_in_scan:
                break




    def gen_object(self, type, send_info = True, id = False):


        if type.team.str_team == self.player_team.str_team:
            type.team = self.player_team
            if type.type == "npc":
                self.sounds["spawn"].stop()
                self.sounds["spawn"].play()
            type.center()

        print("Generating object....")
        obj = type.copy()
        if id:
            obj.id = id
        if type.type == "npc":
            self.render_layers["4.NPCS"].append(obj)
        else:
            self.render_layers["3.BUILDINGS"].append(obj)

        if send_info:
            self.datagatherer.data.append(f"self.game_ref.gen_object({type.gen_string()}, send_info = False, id = {obj.id})")

    def renderobjects(self):

        self.activated_a_object = False

        self.screen.blit(self.images["map"], minus([0, 0], self.camera_pos, op="-"))

        for x in [
            "1.BOTTOM",
            "2.ORE",
            "3.BUILDINGS",
            "4.NPCS",
            "5.CABLE",
            "LOS",
            "activated",
            "6.HUD",
        ]:
            if x == "activated":
                if self.activated_object != None and not self.activated_a_object:
                    self.activated_object.tick()
                continue

            if x == "LOS":
                self.screen.blit(self.los_image, minus([0, 0], self.camera_pos, op="-"))
                continue

            for obj in self.render_layers[x]:
                if obj != self.activated_object:
                    obj.tick()

    def find_object_id(self, id):
        return [x for x in self.return_objects() if x.id == id][0]

    def return_objects(self, list=None):
        objects = []

        if list == None:
            list = self.render_layers.keys()

        for x in list:
            for obj in self.render_layers[x]:
                objects.append(obj)

        return objects

    def get_occupied_slots(self):

        slots = []
        for x in self.render_layers.keys():
            for obj in self.render_layers[x]:
                for x in range(obj.slot_size[0]):
                    for y in range(obj.slot_size[1]):
                        if (
                            core.func.minus(obj.slot, [x, y]) not in slots
                            and obj.type != "deposit"
                        ):
                            slots.append(core.func.minus(obj.slot, [x, y]))
        return slots

    def check_cable_availablity(self, start, end):



        if core.func.get_dist_points(start.center_slot(), end.center_slot()) >= 4.9:
            return False

        for x in self.return_objects(["5.CABLE"]):
            if (x.start_obj == start and x.end_obj == end) or (
                x.start_obj == end and x.end_obj == start
            ):
                return False



        return True

    def calc_energy(self):
        self.player_team.energy_consumption = 0
        self.player_team.energy_generation = 0
        for x in (x for x in self.return_objects() if x.team == self.player_team and (x.connected_to_base or x.name == "Base" or x.type == "npc")):

            for y in x.build_queue:
                self.player_team.energy_consumption += y.energy_consumption
                self.player_team.energy_generation += y.energy_generation

            self.player_team.energy_consumption += x.energy_consumption

            if x.connected_to_base or x.name == "Base":
                self.player_team.energy_generation += x.energy_generation

        self.player_team.c = core.func.towards_target_int(
            self.player_team.c, self.player_team.energy_consumption
        )
        self.player_team.g = core.func.towards_target_int(
            self.player_team.g, self.player_team.energy_generation
        )

    def draw_HUD(self):
        hud_transpose = 0
        if self.activated_object != None:
            hud_transpose = self.activated_object.smoothing
            render_text(
                self,
                self.activated_object.name,
                [17, 20 - hud_transpose],
                80,
                color=self.activated_object.team.color,
            )
            if self.activated_object.type == "npc":
                render_text(
                    self,
                    f"Movement : {self.activated_object.turn_movement}/{self.activated_object.movement_range}",
                    [20, 100 - hud_transpose],
                    30,
                    color=self.activated_object.team.color,
                )
                render_text(
                    self,
                    f"Mode : {self.activated_object.mode}",
                    [20, 130 - hud_transpose],
                    30,
                    color=self.activated_object.team.color,
                )
            elif self.activated_object.type == "building":
                render_text(
                    self,
                    "Connected to network"
                    if self.activated_object.connected_to_base
                    or self.activated_object.name == "Base"
                    else "NOT CONNECTED TO NETWORK",
                    [20, 100 - hud_transpose],
                    30,
                    color=self.activated_object.team.color,
                )

        x, y = self.resolution

        if point_inside(self.mouse_pos, [x - 300, y - 100], [300, 100]):

            render_text(
                self,
                f"CONS. : {self.player_team.energy_consumption} GEN. : {self.player_team.energy_generation}",
                [x - 270, y - 125],
                21,
                color=self.player_team.color,
            )

        self.screen.blit(self.surf, [x - 300, y - 100])

        render_text(
            self,
            self.player_team.name,
            [x - 500, y - 91],
            21,
            color=self.player_team.color,
        )

        if self.player_team.g == 0:
            return
        color = [255, 164, 0]
        if self.player_team.energy_consumption > self.player_team.energy_generation:
            self.generation_overflow_tick.tick()
            if round(self.generation_overflow_tick.value/self.generation_overflow_tick.max_value) == 1:
                color = [255,0,0]


        pygame.draw.rect(
            self.screen,
            color,
            [
                x - 300,
                y - 50,
                300
                * (random.uniform(0, 0.15) + self.player_team.c)
                / self.player_team.g,
                50,
            ],
        )

        self.screen.blit(self.player_team.nrg, [x - 300, y - 100])
        self.screen.blit(self.images["nrg_icon"], [x - 290, y - 100])

        if color == [255,0,0]:
            render_text(
                self,
                f"OVERUSAGE!",
                [x - 150, y - 25,],
                25,
                color=[255, 164, 0],
                centerx = True,
                centery = True
            )



        #

        render_text(
            self,
            f"ENERGY CONSUMPTION",
            [x - 240, y - 91],
            21,
            color=self.player_team.color,
        )

    def loop(self):
        self.state.tick()
        pygame.display.update()
