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


class Menu:
    def __init__(self, game):
        self.game_ref = game
        self.name_box = TextBox(self.game_ref, [250, 20], "Runkkari")
        self.ip_box = TextBox(self.game_ref, [250, 70], "", secret=False)
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
            oneshot_func=self.join_game,
            argument=self.ip_box.text,
        )
        self.exit = Button(
            self.game_ref,
            None,
            3,
            3,
            [255, 0, 0],
            self.game_ref.terminal[50].render("EXIT", True, (255, 255, 255)),
            oneshot=True,
            oneshot_func=self.kill_network,
        )

        self.game_ref.network = None
        self.game_ref.hosting_game = False

    def lobby_host(self, thread, ip):
        time.sleep(1)
        print("SERVER STARTING")
        networking.server.server_run()

    def host_game(self, ip):
        print("HOSTING GAME")
        self.game_ref.hosting_game = True
        try:
            start_new_thread(self.lobby_host, ("1", ip))
            print("Lobby hosted. Joining own lobby")
            self.join_game(ip)
        except Exception as e:
            print("EXCEPTION:", e)

    def join_game(self, ip):
        print("JOINING TO:", ip)
        try:
            self.game_ref.network = Network(ip)
        except Exception as e:
            print("CLIENT: Connection failed")
            print(e)

    def kill_network(self, null):
        self.game_ref.network.send("kill")
        self.game_ref.network = None

    def render_text_boxes(self):
        render_text(self.game_ref, "YOUR NAME:", [20, 20], 30)
        self.name_box.tick()
        render_text(self.game_ref, "JOIN IP:", [20, 70], 30)
        self.ip_box.tick()
        render_text(self.game_ref, f"OWN IP: {self.game_ref.own_ip}", [20, 120], 30)

    def tick(self):
        key_press_manager(self.game_ref)
        self.game_ref.screen.fill(BLACK)
        if self.game_ref.network:

            render_text(self.game_ref, "LOBBY", [20, 20], 30)
            if self.game_ref.hosting_game:
                render_text(self.game_ref, "(HOSTING)", [20, 70], 30)
            self.game_ref.network.send(self.name_box.text)

            self.exit.tick()

        else:

            self.render_text_boxes()
            self.host.tick()
            self.join.tick()
