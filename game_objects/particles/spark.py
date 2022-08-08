import pygame
from game_objects.particles.particle import Particle
import numpy as np

class Spark(Particle):
    def __init__(self, game, pos, velocity):
        super().__init__(game, pos)
        self.velocity = np.array(velocity)
        self.color = [255, 153, 0]
        self.lifetime = 20
