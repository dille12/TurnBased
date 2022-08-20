import pygame
import numpy as np
import random
class UnitStatus:
    def __init__(self, parent, text, size, color):
        self.parent = parent
        self.surface_perm = self.parent.game_ref.terminal[size].render(text, False, color)
        self.angle = 0
        self.game_ref = parent.game_ref
        self.velocity = [random.uniform(-1,1), -1]
        self.pos = parent.slot_to_pos_center()
        self.rotational_velocity = self.velocity[0]*-0.4
        self.lifetime = 60
        self.parent.unitstatuses.append(self)

    def tick(self):
        mult = 1 if self.lifetime <= 55 else (self.lifetime-55)
        self.angle += self.rotational_velocity * mult
        surf_temp = pygame.transform.rotate(self.surface_perm, self.angle)

        if self.lifetime < 20:
            surf_temp.set_alpha(255*self.lifetime/20)
        rx, ry = surf_temp.get_rect().center
        self.pos = [self.pos[0] + self.velocity[0] * mult, self.pos[1] + self.velocity[1] * mult]
        pos = [self.pos[0] - rx, self.pos[1] - ry]
        self.game_ref.screen.blit(surf_temp, self.game_ref.get_pos(pos))
        self.lifetime -= 1
        self.velocity[0] *= 0.99
        self.velocity[1] *= 0.99
        self.rotational_velocity *= 0.99
        if self.lifetime == 0:
            self.parent.unitstatuses.remove(self)
