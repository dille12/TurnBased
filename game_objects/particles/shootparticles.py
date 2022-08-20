import pygame
from game_objects.particles.particle import Particle
import numpy as np
import random

class ShootParticle(Particle):
    def __init__(self, game, pos, velocity):
        super().__init__(game, pos)
        self.velocity = np.array(velocity)
        self.color = [255, 153, 0]
        self.lifetime = random.randint(3,20)
        self.lt_instart = self.lifetime
        self.size = 3

    def tick(self):
        self.height_manipulation()
        self.vibrate(amount = self.lifetime)
        self.render_alt()
        self.lt()

    def render_alt(self):
        self.pos += (self.velocity*self.lifetime/self.lt_instart)
        self.dim = [self.pos[0]-round(self.lifetime/2), self.pos[1]-round(self.lifetime/2), self.lifetime,self.lifetime]
        self.color = [255,255 - 255/self.lifetime ,0]

        pygame.draw.rect(
            self.game_ref.screen,
            self.color,
            [
                self.dim[0] - self.game_ref.camera_pos[0],
                self.dim[1] - self.game_ref.camera_pos[1],
                self.dim[2],
                self.dim[3],
            ],
        )
