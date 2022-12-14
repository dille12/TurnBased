import pygame
from game_objects.game_object import Game_Object
from core.func import *
from core.image_transform import *


class Deposit(Game_Object):
    def __init__(self, game, team, name, slot, movement_range=3, hp=100, image=None):
        super().__init__(game, team, name=name, slot=slot, hp=hp)

        self.image = pygame.transform.rotate(
            self.game_ref.images["depo"].copy(), 90 * random.randint(0, 3)
        )
        self.type = "deposit"

    def tick(self):
        self.render(self)
