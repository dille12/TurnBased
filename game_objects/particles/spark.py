import pygame
from game_objects.particles.particle import Particle
import numpy as np
from random import uniform, randint


class Spark(Particle):
    def __init__(self, game, pos, velocity):
        super().__init__(game, pos)
        self.velocity = np.array(velocity)
        self.color = [255, 153, 0]
        self.lifetime = 20
        self.size = 3

    def tick(self):
        self.size = self.lifetime / 4

        self.height_manipulation()

        self.vibrate()
        self.render()
        self.lt()
