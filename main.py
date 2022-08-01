import pygame
from gameclass import Game

game = Game([1920,1080])
#game = Game([640,360])
#game = Game([1280 , 720])

while 1:
    game.clock.tick(60)
    game.loop()
