import pygame
from game_objects.particles.particle import Particle
import numpy as np
from random import uniform, randint
import core.func


class Ash(Particle):
    def __init__(self, game, pos, velocity=None):
        super().__init__(game, pos)
        self.velocity = np.array([uniform(-20, 20), uniform(-20, 20)])
        self.color = [40, 40, 40]
        self.lifetime = randint(6, 14)
        self.size = 0

    def tick(self):
        try:
            self.color = core.func.mult(self.color, 1.05)
        except:
            pass

        self.size = self.lifetime * 2.5
        self.pos += self.velocity * self.size / 20
        self.vibrate()
        self.render_to_ground()
        self.lt()

    def render_to_ground(self):
        rect = pygame.Rect(
            self.pos[0] - self.size / 2,
            self.pos[1] - self.size / 2,
            self.size,
            self.size,
        )
        pygame.draw.rect(self.game_ref.images["map"], self.color, rect)
