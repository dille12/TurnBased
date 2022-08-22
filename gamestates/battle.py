import pygame
from core.keypress import *
from core.camera_movement import *
import numpy as np
from values import *
from core.func import *
from game_objects.game_object import Game_Object
from game_objects.npc import NPC
from game_objects.building import Building
from game_objects.objects import *
from hud_elements.battle_hud import draw_HUD

from core.map_gen import *


class Battle:
    def __init__(self, game):
        self.game_ref = game

        self.game_ref.next_turn_button = Button(
            self.game_ref,
            self.game_ref,
            17,
            8.5,
            self.game_ref.player_team.color,
            self.game_ref.images["nextturn"],
            oneshot=True,
            oneshot_func=self.game_ref.end_turn,
        )

        self.game_ref.turn = self.game_ref.connected_players[0]

        spawns = [[1, 1], [22, 22], [2, 17], [20, 6]]

        if self.game_ref.hosting_game:
            for team in self.game_ref.connected_players:
                print(team == self.game_ref.player_team)
                slot = pick_random_from_list(spawns)
                print("Building a base for team", team.color)

                self.game_ref.gen_object(Base(self.game_ref, team, slot))

                # self.render_layers["3.BUILDINGS"].append(Building(self,team,"Base",slot, image = self.images["base"].copy(), size = [2,2]))
                spawns.remove(slot)
            random_gen_mines(self.game_ref)
            gen_mines(self.game_ref)
            self.game_ref.datagatherer.data.append(
                f"self.game_ref.set_mines({self.game_ref.mines})"
            )

        for x in self.game_ref.connected_players:
            x.nrg = colorize(self.game_ref.images["nrg_icon"], pygame.Color(x.color))

        pygame.mixer.music.stop()

    def tick(self):
        self.game_ref.calc_energy()

        self.game_ref.datagatherer.tick()

        key_press_manager(self.game_ref)
        if not self.game_ref.chat.chatbox.active:
            cam_movement(self.game_ref)

        self.game_ref.delta = np.array(self.game_ref.prev_pos) - np.array(
            self.game_ref.camera_pos
        )
        self.game_ref.prev_pos = self.game_ref.camera_pos.copy()

        # self.game_ref.camera_pos = minus(self.game_ref.mouse_pos,[0.3,0.3], op = "*")
        self.game_ref.screen.fill(BLACK)
        self.game_ref.renderobjects()
        self.game_ref.tick_animations()
        draw_HUD(self.game_ref)
        self.game_ref.own_turn = False
        if self.game_ref.turn == self.game_ref.player_team:
            self.game_ref.own_turn = True
            self.game_ref.next_turn_button.tick()

        self.game_ref.tick_alert()

        print_s(self.game_ref, f"FPS:{self.game_ref.fps}", 1)
        print_s(self.game_ref, f"IDLE:{self.game_ref.idle}%", 2)
        ping = 0
        for i in self.game_ref.ping:
            ping += i

        ping /= len(self.game_ref.ping)

        print_s(self.game_ref, f"PING:{round(ping*1000)}ms", 3)
