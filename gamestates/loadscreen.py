from _thread import *
import pygame
from core.load import load
from values import *
from core.func import render_text


class Loadscreen:
    def __init__(self, game):
        self.game_ref = game

        start_new_thread(load, (self.game_ref,))

    def tick(self):
        self.game_ref.screen.fill(BLACK)
        pygame.draw.rect(
            self.game_ref.screen,
            [255, 255, 255],
            [
                0,
                self.game_ref.resolution[1] - 30,
                self.game_ref.resolution[0] * (self.game_ref.load_i / 46),
                30,
            ],
        )
        try:
            render_text(self.game_ref, f"Now loading: {self.game_ref.loading}", [20,self.game_ref.resolution[1] - 80],30)
        except:
            pass
