import pygame
import core.func

def cam_movement(game):
    if "mouse2"in game.keypress:
        game.cam_moving = True
        game.cam_origin = game.mouse_pos.copy()

    elif not "mouse2" in game.keypress_held_down:
        game.cam_moving = False

    if game.cam_moving:
        game.camera_pos_target = core.func.minus(game.camera_pos_target, core.func.minus(game.cam_origin, game.mouse_pos, op = "-"))
        game.cam_origin = game.mouse_pos.copy()


    # if "d" in game.keypress:
    #     game.camera_pos_target[0] += 500
    # if "a" in game.keypress:
    #     game.camera_pos_target[0] -= 500
    # if "s" in game.keypress:
    #     game.camera_pos_target[1] += 500
    # if "w" in game.keypress:
    #     game.camera_pos_target[1] -= 500


    game.camera_pos = core.func.minus(game.camera_pos, core.func.minus(core.func.minus(game.camera_pos_target, game.camera_pos, op = "-"), [0.45,0.45], op="*"))
