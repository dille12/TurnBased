import pygame
from main import Game
import time
import socket

game = Game([1920, 1080])

# game = Game([640,360])
# game = Game([1280 , 720])
fps_update = time.time()
while 1:
    t1 = time.time()
    game.clock.tick(60)
    t = time.time()
    game.loop()

    if time.time() - fps_update > 0.25:
        game.fps = round(1 / (time.time() - t))
        game.idle = 100 - round((time.time() - t) * 100 / ((time.time() - t1)))
        fps_update = time.time()
