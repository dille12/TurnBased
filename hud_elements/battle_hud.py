import pygame
from core.func import *

def draw_HUD(game):
    hud_transpose = 0
    if game.activated_object != None:
        hud_transpose = game.activated_object.smoothing

        game.screen.blit(game.images["hud_sprite_1"], [0,-hud_transpose])

        render_text_glitch(
            game,
            game.activated_object.name,
            [17, 22 - hud_transpose],
            80,
            color=game.activated_object.team.color,
            glitch = 4
        )
        if game.activated_object.type == "npc":
            render_text_glitch(
                game,
                f"Movement : {game.activated_object.turn_movement}/{game.activated_object.movement_range}",
                [20, 102 - hud_transpose],
                30,
                color=game.activated_object.team.color,
                glitch = 2
            )
            render_text_glitch(
                game,
                f"Mode : {game.activated_object.mode}",
                [20, 129 - hud_transpose],
                30,
                color=game.activated_object.team.color,
                glitch = 2
            )
        elif game.activated_object.type == "building":
            render_text_glitch(
                game,
                "Connected to network"
                if game.activated_object.connected_to_base
                or game.activated_object.name == "Base"
                else "NOT CONNECTED TO NETWORK",
                [20, 102 - hud_transpose],
                30,
                color=game.activated_object.team.color,
                glitch = 2
            )
            if hasattr(game.activated_object, "resource"):
                res = game.activated_object.resource
                render_text_glitch(
                    game,
                    res if res != "" else "???",
                    [20, 129 - hud_transpose],
                    30,
                    color=[255,0,0] if res == "Iridium" else [0,255,0] if res == "Uranium" else [51, 204, 255] if res == "Tungsten" else [255, 102, 0],
                    glitch = 2
                )

    x, y = game.resolution

    if point_inside(game.mouse_pos, [x - 300, y - 100], [300, 100]):

        render_text(
            game,
            f"CONS. : {game.player_team.energy_consumption} GEN. : {game.player_team.energy_generation}",
            [x - 270, y - 125],
            21,
            color=game.player_team.color,
        )

    game.screen.blit(game.surf, [x - 300, y - 100])

    render_text(
        game,
        game.player_team.name,
        [x - 500, y - 91],
        21,
        color=game.player_team.color,
    )

    if game.player_team.g == 0:
        return
    color = [255, 164, 0]
    if game.player_team.energy_consumption > game.player_team.energy_generation:
        game.generation_overflow_tick.tick()
        if round(game.generation_overflow_tick.value/game.generation_overflow_tick.max_value) == 1:
            color = [255,0,0]


    pygame.draw.rect(
        game.screen,
        color,
        [
            x - 300,
            y - 50,
            300
            * (random.uniform(0, 0.15) + game.player_team.c)
            / game.player_team.g,
            50,
        ],
    )

    game.screen.blit(game.player_team.nrg, [x - 300, y - 100])
    game.screen.blit(game.images["nrg_icon"], [x - 290, y - 100])

    if color == [255,0,0]:
        render_text(
            game,
            f"OVERUSAGE!",
            [x - 150, y - 25,],
            25,
            color=[255, 164, 0],
            centerx = True,
            centery = True
        )



    #

    render_text(
        game,
        f"ENERGY CONSUMPTION",
        [x - 240, y - 91],
        21,
        color=game.player_team.color,
    )