import pygame
from main import Game
import time
import socket

game = Game([1920, 1080], draw_los=False)

# game = Game([640,360])
# game = Game()
fps_update = time.time()
while 1:
    t1 = time.time()
    game.clock.tick(60)
    t = time.time()
    game.loop()

    try:
        game.fps = round(game.clock.get_fps())
        if time.time() - fps_update > 0.25:

            game.idle = 100 - round((time.time() - t) * 100 / ((time.time() - t1)))
            fps_update = time.time()
    except:
        pass
