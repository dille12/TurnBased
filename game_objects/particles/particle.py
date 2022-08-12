import pygame
import numpy as np
from values import *
from random import uniform, randint


class Particle:
    def __init__(self, game, pos):
        self.game_ref = game
        self.pos = np.array(pos)
        self.height = 0
        self.height_velocity = -5
        self.team = nature
        self.type = "particle"
        self.slot_size = [-1, -1]
        self.id = -1

    def height_manipulation(self, bounce=True):
        self.pos += self.velocity
        self.height += self.height_velocity
        self.height_velocity += 0.5

        if self.height > 0 and bounce:
            self.height_velocity *= -0.75
            self.height -= 1

    def lt(self):
        self.lifetime -= 1
        if self.lifetime < 1:
            self.kill()

    def vibrate(self, amount=2):

        self.pos += np.array([randint(-amount, amount), randint(-amount, amount)])

    def render(self):
        pygame.draw.rect(
            self.game_ref.screen,
            self.color,
            [
                self.pos[0] - self.game_ref.camera_pos[0] - self.size / 2,
                self.pos[1] - self.game_ref.camera_pos[1] + self.height - self.size / 2,
                self.size,
                self.size,
            ],
        )

    def kill(self):
        self.game_ref.render_layers["PARTICLES"].remove(self)
