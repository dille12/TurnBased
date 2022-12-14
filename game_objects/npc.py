import pygame
from game_objects.game_object import Game_Object
from core.func import *
from core.image_transform import *
from hud_elements.button import *


class NPC(Game_Object):
    def __init__(self, game, team, name, slot, movement_range=3, hp=100, image=None):
        super().__init__(game, team, name=name, slot=slot, hp=hp)
        self.type = "npc"
        self.movement_range = movement_range
        self.turn_movement = movement_range
        self.routes = []
        self.moving_route = []
        self.move_tick = game.GT(20)
        self.render_long_routes = False
        self.stashed_route = []
        self.target = None
        self.image = image
        self.target_pos = [0,0]

        self.battery_life_max = 8
        self.battery_life = self.battery_life_max
        self.build = None
        if self.image != None:
            self.image = colorize_alpha(
                image.copy(),
                pygame.Color(
                    self.team.color[0], self.team.color[1], self.team.color[2]
                ),
                50,
            )
            self.image_bg = colorize_alpha(image.copy(), pygame.Color(0, 0, 0), 100)

        self.check_mode()

    def npc_build(self, type):
        print("Building")

        self.occ_slots = self.game_ref.get_occupied_slots()

        # if type == "elec_tower":
        self.build = type
        self.build.c_building = True

    def move(self):

        if self.target == None:
            self.target = self.slot.copy()

        if self.turn_movement > 0 and (not self.own() or self.battery_life > 0) and self.moving_route != []:



            if self.move_tick.tick():
                self.slot = self.target.copy()
                self.moving_route.remove(self.moving_route[0])
                if self.moving_route == []:
                    return
                self.target = self.moving_route[0]

                list_play(
                    [
                        self.game_ref.sounds["walk1"],
                        self.game_ref.sounds["walk2"],
                        self.game_ref.sounds["walk3"],
                    ]
                )

                self.turn_movement -= 1
                self.battery_life -= 1
                self.los()

                print(self.moving_route)

        elif self.own() and self.battery_life == 0:
            self.moving_route = []
            self.stashed_route = []

        elif self.moving_route != []:
            self.stashed_route = self.moving_route.copy()
            self.moving_route = []

        self.slot = minus(
            self.slot,
            minus(minus(self.target, self.slot, op="-"), [0.6, 0.6], op="*"),
        )

        if self.stashed_route != [] and self.active and self.own():
            self.render_lines_route(route = self.stashed_route)



    def update_routes(self):
        self.routes = self.scan_movement(self.turn_movement)

    def movement_tick(self):
        pass

    def movement_and_attack_tick(self):
        if self.build == None:

            if self.mode == "walk":

                if self.active and "mouse2" in self.game_ref.keypress and self.game_ref.own_turn:
                    self.render_long_routes = True
                    self.stashed_route = []
                    self.game_ref.sounds["walking_s"].play()

                if self.render_long_routes:
                    if "mouse2" not in self.game_ref.keypress_held_down:
                        self.game_ref.sounds["walking_e"].play()
                        if len(self.route_to_pos) > 1:
                            self.moving_route = self.route_to_pos.copy()[:self.battery_life+1]
                            self.route_to_pos = []
                            #self.activate(False)
                            self.send_info(["moving_route", "turn_movement"])
                            self.render_long_routes = False
                        else:
                            self.render_long_routes = False
                            self.moving_route = []
                            self.route_to_pos = []


                    self.render_long_range()

            elif self.mode == "attack" and self.active and self.shots > 0:

                self.scan_enemies()

                x, y = self.slot_to_pos_c(minus(self.slot, [-self.range, -self.range]))
                size = (1 + self.range * 2) * self.game_ref.ss

                pygame.draw.rect(
                    self.game_ref.screen, [255, 0, 0], [x, y, size, size], 2
                )



                self.tick_action(self.attack, text = "ATTACK", argument = round(-50 * (self.battery_life/self.battery_life_max)))

            elif self.mode == "sabotage" and self.active and self.shots > 0:
                self.scan_enemies(include = {"type" : "building"}, exclude = {"name" : "Base"})
                x, y = self.slot_to_pos_c(minus(self.slot, [-self.range, -self.range]))
                size = (1 + self.range * 2) * self.game_ref.ss
                pygame.draw.rect(
                    self.game_ref.screen, [255, 0, 0], [x, y, size, size], 2
                )

                self.tick_action(self.shortcircuit, text = "SHORTCIRCUIT", argument = round(random.uniform(0, (self.battery_life/self.battery_life_max))))





    def tick(self):
        self.los()

        if self.moving_route == []:
            self.click()

        self.activation_smoothing()

        self.movement_and_attack_tick()

        if "esc" in self.game_ref.keypress:
            self.activate(False)


        self.move()

        self.render(self)

        if self.build != None:

            self.build.tick_buildable(self.occ_slots)

            if "mouse0" in self.game_ref.keypress and self.build.able_to_place:
                self.game_ref.gen_object(self.build)
                self.build = None
                self.update_routes()

        else:

            self.tick_buttons()
        self.tick_statuses()

        self.delete()
