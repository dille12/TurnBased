import pygame
from core.keypress import *
from core.camera_movement import *
import numpy as np
from values import *
from core.func import *


class Battle:
    def __init__(self, game):
        self.game_ref = game
        pass

    def tick(self):
        self.game_ref.calc_energy()

        key_press_manager(self.game_ref)
        cam_movement(self.game_ref)

        self.game_ref.delta = np.array(self.game_ref.prev_pos) - np.array(
            self.game_ref.camera_pos
        )
        self.game_ref.prev_pos = self.game_ref.camera_pos.copy()

        # self.game_ref.camera_pos = minus(self.game_ref.mouse_pos,[0.3,0.3], op = "*")
        self.game_ref.screen.fill(BLACK)
        self.game_ref.renderobjects()
        self.game_ref.draw_HUD()
        self.game_ref.next_turn_button.tick()

        print_s(self.game_ref, f"FPS:{self.game_ref.fps}", 1)
        print_s(self.game_ref, f"IDLE:{self.game_ref.idle}%", 2)
