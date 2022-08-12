import pygame
from texture.texture import load_images
from sounds.sounds import load_sounds
from game_objects.game_object import *
from game_objects.npc import *
from game_objects.building import *
from game_objects.wall import *
from game_objects.deposit import *
from game_objects.mine import *
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
from hud_elements.chat import Chat
import gamestates.battle
import gamestates.menu
import gamestates.loadscreen

import socket
from networking.datagatherer import DataGatherer


class Game:

    """
    Game class to contain all information for ease of access.
    """

    def __init__(self, resolution, draw_los=True):
        pygame.init()
        pygame.font.init()
        self.draw_los = draw_los
        self.GT = GameTick

        self.datagatherer = DataGatherer(self)

        self.load_i = 0

        self.resolution = resolution
        self.loading = ""

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
        self.chat = Chat(self)
        self.connected_players = []
        self.notification_tick = self.GT(180, oneshot=True)
        self.notification = ""
        self.notification_color = [255, 255, 255]
        self.vibration = 0

        self.qsc = 1920 / resolution[0]

        self.ss = 100 * self.qsc  # SLOT SIZE
        self.smoothing = 0

        self.screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)

        self.render_layers = {
            "1.BOTTOM": [],
            "2.ORE": [],
            "3.BUILDINGS": [],
            "4.NPCS": [],
            "PARTICLES": [],
            "5.CABLE": [],
            "6.HUD": [],
        }

        self.own_turn = True
        self.keypress = []
        self.keypress_held_down = []
        self.cam_moving = False
        self.timedelta = 1
        self.activated_object = None
        self.fps = 0
        self.idle = 0
        self.iridium_mined = 0

        self.clock = pygame.time.Clock()

        self.state = gamestates.loadscreen.Loadscreen(self)

    def get_pos(self, pos):
        # return minus(pos,self.camera_pos, op = "-")
        return minus(minus(pos, self.camera_pos, op="-"), self.size_conv, op="/")

    def get_pos_rev(self, pos):
        return minus(minus(pos, self.camera_pos, op="+"), self.size_conv, op="/")

    def set_mines(self, mines):
        self.mines = mines
        gen_mines(self)

    def set_notification(self, text, color=[255, 255, 255]):
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
                if x.c_build_time > 0 and x.connected_building():
                    x.c_build_time -= 1

    def end_turn(self, arg):
        self.scan_connecting_cables()
        if self.draw_los:
            self.los_image.fill([0, 0, 0])
            for x in self.return_objects():
                if x.type == "building":
                    x.los()

        for i, x in enumerate(self.connected_players):
            if x == self.player_team:

                if i == len(self.connected_players) - 1:
                    next_player = self.connected_players[0]
                else:
                    next_player = self.connected_players[i + 1]

                self.set_turn(next_player.str_team, send_info=True)
                print("Next turn is", next_player)

                return

    def set_turn(self, player, send_info=False):
        for x in self.connected_players:
            if x.str_team == player:
                self.turn = x

                if send_info:
                    self.datagatherer.data.append(
                        f'self.game_ref.set_turn("{x.str_team}")'
                    )

                if self.player_team.str_team == x.str_team:
                    print("own turn")
                    self.begin_turn()
                self.sounds["turn_change"].stop()
                self.sounds["turn_change"].play()
                self.set_notification(f"{x.name}'s turn", color=x.color)

                return

    def tick_alert(self):
        if not self.notification_tick.tick() and self.notification_tick.value > 20:
            if self.notification == "":
                return
            tick = self.notification_tick.value - 20
            alpha = 255
            if tick < 40:
                alpha = 255 * tick / 40

            elif 160 > tick > 100:
                alpha = 255 * (160 - tick) / 60

            text = self.terminal[100].render(
                self.notification, False, self.notification_color
            )
            text.set_alpha(alpha)
            size_1 = round(text.get_size()[1] * (alpha / 255) ** 5 + 5)
            surf = pygame.Surface((self.resolution[0], size_1)).convert()
            surf.fill(core.func.mult(self.notification_color, (0.15)))
            surf.set_alpha((alpha / 255) ** 5 * 255)
            pos = [
                self.resolution[0] / 2 - text.get_rect().center[0],
                self.resolution[1] / 3 - text.get_rect().center[1],
            ]
            self.screen.blit(
                surf, [0, pos[1] + text.get_size()[1] / 2 - surf.get_size()[1] / 2]
            )

            self.screen.blit(text, pos)

    def slot_inside(self, slot):
        return 0 <= slot[0] < self.size_slots[0] and 0 <= slot[1] < self.size_slots[1]

    def scan_connecting_cables(self):
        print("Scanning cablenetwork")
        self.connected_in_scan = 0
        for x in self.render_layers["3.BUILDINGS"]:
            if x.team == self.player_team:
                x.connected_to_base = False
                if x.name == "Base":
                    base = x
                    x.connected_to_base = True

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

    def gen_object(self, type, send_info=True, id=False):

        if type.team.str_team == self.player_team.str_team:
            type.team = self.player_team
            if type.type == "npc":
                self.sounds["spawn"].stop()
                self.sounds["spawn"].play()
            self.chat.append(f"{type.name} built.")
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
            self.datagatherer.data.append(
                f"self.game_ref.gen_object({type.gen_string()}, send_info = False, id = {obj.id})"
            )

    def vibrate(self):
        if self.vibration > 0:
            self.camera_pos = [
                self.camera_pos[0] + random.randint(-self.vibration, self.vibration),
                self.camera_pos[1] + random.randint(-self.vibration, self.vibration),
            ]
            self.vibration -= 1

    def renderobjects(self):

        self.activated_a_object = False

        self.screen.blit(self.images["map"], minus([0, 0], self.camera_pos, op="-"))

        for x in [
            "1.BOTTOM",
            "2.ORE",
            "3.BUILDINGS",
            "4.NPCS",
            "PARTICLES",
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
                if self.draw_los:
                    self.screen.blit(
                        self.los_image, minus([0, 0], self.camera_pos, op="-")
                    )
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
                            and obj.type != "mine"
                        ):
                            slots.append(core.func.minus(obj.slot, [x, y]))
        return slots

    def cut_cable(self, id):
        for x in self.return_objects(["5.CABLE"]):
            if x.id == id:
                self.render_layers["5.CABLE"].remove(x)
                return

    def check_cable_availablity(self, start, end):

        if core.func.get_dist_points(start.center_slot(), end.center_slot()) > 5:
            return False

        return True

    def cable_exists(self, start, end):
        for x in self.return_objects(["5.CABLE"]):
            if (x.start_obj == start and x.end_obj == end) or (
                x.start_obj == end and x.end_obj == start
            ):
                return x
        return False

    def calc_energy(self):
        self.player_team.energy_consumption = 0
        self.player_team.energy_generation = 0
        for x in (
            x
            for x in self.return_objects()
            if x.team == self.player_team
            and (x.connected_to_base or x.name == "Base" or x.type == "npc")
        ):

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

    def loop(self):
        self.state.tick()
        self.chat.tick()
        self.vibrate()
        pygame.display.update()
