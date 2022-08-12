import pygame
from core.keypress import *
from core.camera_movement import *
import numpy as np
from values import *
from core.func import *
from hud_elements.button import Button
from hud_elements.textbox import TextBox
from networking.network import *
from networking.server import *
from networking.connect import *
from networking.network import Network
from _thread import *
import networking.server
import time
import random
import ast
import gamestates.battle
import math


class Menu:
    def __init__(self, game):
        self.game_ref = game
        self.name_box = TextBox(
            self.game_ref, [250, 20], f"Runkkari{random.randint(0,100)}"
        )
        self.ip_box = TextBox(
            self.game_ref, [250, 70], self.game_ref.own_ip, secret=False
        )
        self.threading = False
        self.glitch_amount = 2
        self.menu_text = "MAIN MENU"
        self.button_click_tick = self.game_ref.GT(30, oneshot=True)
        self.host = Button(
            self.game_ref,
            None,
            0.5,
            3,
            [255, 0, 0],
            self.game_ref.terminal[50].render("HOST", True, (255, 255, 255)),
            oneshot=True,
            oneshot_func=self.host_game,
            argument=self.game_ref.own_ip,
        )
        self.join = Button(
            self.game_ref,
            None,
            3,
            3,
            [255, 0, 0],
            self.game_ref.terminal[50].render("JOIN", True, (255, 255, 255)),
            oneshot=True,
            oneshot_func=self.join_game_from_ip,
            argument=None,
        )
        self.start = Button(
            self.game_ref,
            None,
            0.5,
            3,
            [255, 0, 0],
            self.game_ref.terminal[50].render("START GAME", True, (255, 255, 255)),
            oneshot=True,
            oneshot_func=self.start_game,
            argument=None,
        )
        self.exit = Button(
            self.game_ref,
            None,
            4,
            3,
            [255, 0, 0],
            self.game_ref.terminal[50].render("EXIT", True, (255, 255, 255)),
            oneshot=True,
            oneshot_func=self.kill_network,
        )

        self.game_ref.network = None
        self.game_ref.hosting_game = False

        pygame.mixer.music.load("sounds/music/game_loop.mp3")
        pygame.mixer.music.set_volume(self.game_ref.music_volume)
        pygame.mixer.music.play(-1)

    def lobby_host(self, thread, ip):
        print("SERVER STARTING")
        self.game_ref.server = networking.server.Server(self.game_ref)

    def get_names(self):
        list = []
        for x in self.game_ref.connected_players:
            list.append(x.name)
        return list

    def threaded_player_info_gathering(self):
        self.threading = True
        reply = self.game_ref.network.send(self.name_box.text)

        if "STARTGAME" in reply.split("/"):
            print("Client reveived start order")
            self.start_game(None)
            return

        for x in reply.split("/"):
            y = x.split("-")
            if y[0] == "" or y[0] in self.get_names() or len(y) == 1:
                continue

            print("Player connected:", y[0])

            team = Player(ast.literal_eval(y[1]), y[0], y[2])

            self.game_ref.connected_players.append(team)
            if y[0] == self.name_box.text and self.game_ref.player_team == placeholder:
                print("Assigning to player team")
                self.game_ref.player_team = team

        self.threading = False

    def host_game(self, ip):
        print("HOSTING GAME")
        self.game_ref.hosting_game = True
        try:
            start_new_thread(self.lobby_host, ("1", ip))
            print("Lobby hosted. Joining own lobby")
            self.join_game(ip)
        except Exception as e:
            self.game_ref.error_message = e

    def join_game(self, ip):
        print("JOINING TO:", ip)
        try:
            self.game_ref.network = Network(ip, self.game_ref)
        except Exception as e:
            self.game_ref.error_message = e

    def join_game_from_ip(self, arg):
        ip = self.ip_box.text
        print("JOINING TO:", ip)
        try:
            self.game_ref.network = Network(ip, self.game_ref)
        except Exception as e:
            self.game_ref.error_message = e

    def kill_network(self, null):
        self.game_ref.network.send("kill")
        self.game_ref.network = None

    def start_game(self, null):

        self.game_ref.network.send("/STARTGAME/")

        print(
            "PLAYER TEAM:",
            self.game_ref.player_team.color,
            self.game_ref.player_team.name,
        )
        self.game_ref.state = gamestates.battle.Battle(self.game_ref)

    def render_text_boxes(self):
        render_text(self.game_ref, "YOUR NAME:", [20, 20], 30)
        self.name_box.tick()
        render_text(self.game_ref, "JOIN IP:", [20, 70], 30)
        self.ip_box.tick()
        render_text(
            self.game_ref,
            f"OWN IP: {self.game_ref.own_ip}",
            [20 - self.smoothing, 120],
            30,
        )

    def lobby_tick(self):
        render_text(self.game_ref, "LOBBY", [20, 20], 30)
        if self.game_ref.hosting_game:
            render_text(self.game_ref, "(HOSTING)", [20, 70], 30)
            self.start.tick()
        if not self.threading:
            start_new_thread(self.threaded_player_info_gathering, ())
        i = 0
        for x in self.game_ref.connected_players:
            render_text(self.game_ref, x.name, [20, 130 + i], 30, color=x.color)
            i += 30

        self.exit.tick()

    def tick_recovery(self):
        if not self.button_click_tick.tick():
            self.smoothing = (
                1
                + math.cos(
                    math.pi
                    * self.button_click_tick.value
                    / self.button_click_tick.max_value
                )
            ) * 100
        else:
            self.smoothing = 0

    def tick(self):
        self.tick_recovery()
        key_press_manager(self.game_ref)
        self.game_ref.screen.fill(BLACK)
        if self.game_ref.network:
            self.lobby_tick()
        else:
            self.render_text_boxes()
            self.host.tick()
            self.join.tick()

        if self.game_ref.error_message != None:
            render_text(
                self.game_ref,
                self.game_ref.error_message,
                [20, 600],
                30,
                color=[255, 0, 0],
            )
            if time.time() - self.error_time > 5:
                self.game_ref.error_message = None
        else:
            self.error_time = time.time()
        if "mouse0" in self.game_ref.keypress:
            self.glitch_amount = 30
            self.button_click_tick.value = 0

        render_text_glitch(
            self.game_ref,
            self.menu_text,
            [self.game_ref.resolution[0] / 2, 20],
            100,
            centerx=True,
            glitch=self.glitch_amount,
        )
        if self.glitch_amount >= 4:
            self.glitch_amount -= 1
