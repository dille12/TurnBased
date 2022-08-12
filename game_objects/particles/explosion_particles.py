import pygame
from game_objects.particles.particle import Particle
import numpy as np
from random import uniform, randint
import core.func


class ExplosionParticle(Particle):
    def __init__(self, game, pos, velocity=None):
        super().__init__(game, pos)
        self.velocity = np.array([uniform(-50, 50), uniform(-50, 50)])
        self.color = [255, 153, 51]
        self.lifetime = randint(10, 20)
        self.size = 0

    def tick(self):
        self.color[1:2] = core.func.mult(self.color, 0.9)[1:2]

        self.size = self.lifetime

        self.height_manipulation(bounce=False)

        self.render()

        self.lt()
