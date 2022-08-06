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


class Menu:
    def __init__(self, game):
        self.game_ref = game
        self.name_box = TextBox(self.game_ref, [250, 20], f"Runkkari{random.randint(0,100)}")
        self.ip_box = TextBox(self.game_ref, [250, 70], "25.90.55.6", secret=False)
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

    def lobby_host(self, thread, ip):
        print("SERVER STARTING")
        networking.server.server_run()

    def get_names(self):
        list = []
        for x in self.game_ref.connected_players:
            list.append(x.name)
        return list

    def threaded_player_info_gathering(self):
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

            team = Player(
                ast.literal_eval(y[1]),
                y[0],
                y[2]
                )



            self.game_ref.connected_players.append(team)
            if y[0] == self.name_box.text and self.game_ref.player_team == placeholder:
                print("Assigning to player team")
                self.game_ref.player_team = team







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

        print("PLAYER TEAM:",self.game_ref.player_team.color, self.game_ref.player_team.name)
        self.game_ref.state = gamestates.battle.Battle(self.game_ref)


    def render_text_boxes(self):
        render_text(self.game_ref, "YOUR NAME:", [20, 20], 30)
        self.name_box.tick()
        render_text(self.game_ref, "JOIN IP:", [20, 70], 30)
        self.ip_box.tick()
        render_text(self.game_ref, f"OWN IP: {self.game_ref.own_ip}", [20, 120], 30)


    def lobby_tick(self):
        render_text(self.game_ref, "LOBBY", [20, 20], 30)
        if self.game_ref.hosting_game:
            render_text(self.game_ref, "(HOSTING)", [20, 70], 30)
            self.start.tick()

        start_new_thread(self.threaded_player_info_gathering, ())
        i = 0
        for x in self.game_ref.connected_players:
            render_text(self.game_ref, x.name, [20, 130+i], 30, color = x.color)
            i+=30


        self.exit.tick()


    def tick(self):
        key_press_manager(self.game_ref)
        self.game_ref.screen.fill(BLACK)
        if self.game_ref.network:
            self.lobby_tick()
        else:
            self.render_text_boxes()
            self.host.tick()
            self.join.tick()

        if self.game_ref.error_message != None:
            render_text(self.game_ref, self.game_ref.error_message, [20, 600], 30, color = [255,0,0])
            if time.time() - self.error_time > 5:
                self.game_ref.error_message = None
        else:
            self.error_time = time.time()
