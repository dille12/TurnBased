import pygame
import core.func

def cam_movement(game):
    if "mouse1"in game.keypress:
        game.cam_moving = True
        game.cam_origin = game.mouse_pos.copy()

    elif not "mouse1" in game.keypress_held_down:
        game.cam_moving = False

    if game.cam_moving:
        game.camera_pos_target = core.func.minus(game.camera_pos_target, core.func.minus(game.cam_origin, game.mouse_pos, op = "-"))
        game.cam_origin = game.mouse_pos.copy()

    camera_movement = 30
    if game.mouse_pos[0] > game.resolution[0] - 10 or "d" in game.keypress_held_down:
        game.camera_pos_target[0] += camera_movement
    elif game.mouse_pos[0] < 10 or "a" in game.keypress_held_down:
        game.camera_pos_target[0] -= camera_movement

    if game.mouse_pos[1] > game.resolution[1] - 10 or "s" in game.keypress_held_down:
        game.camera_pos_target[1] += camera_movement
    elif game.mouse_pos[1] < 10 or "w" in game.keypress_held_down:
        game.camera_pos_target[1] -= camera_movement

    camera_panning = 0.15

    game.camera_pos = core.func.minus(game.camera_pos, core.func.minus(core.func.minus(game.camera_pos_target, game.camera_pos, op = "-"), [camera_panning,camera_panning], op="*"))
