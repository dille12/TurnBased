import pygame
from game_objects.game_object import Game_Object
from core.func import *
from core.image_transform import *
from game_objects.cable import *
from hud_elements.button import *
import numpy as np
import math


class Building(Game_Object):
    def __init__(self, game, team, name, slot, hp=1000, image=None, size=[1, 1]):
        super().__init__(game, team, name=name, slot=slot, hp=hp, size=size)
        self.type = "building"
        self.image = image
        self.cable = None
        self.static_cables = []
        self.top_layer = None

        self.connected_cables = []

        self.cable_send_tick = self.game_ref.GT(45)

        self.c_building = False

        if self.image != None:
            self.image = colorize_alpha(
                image.copy(),
                pygame.Color(
                    self.team.color[0], self.team.color[1], self.team.color[2]
                ),
                50,
            )

            self.placeable = colorize_alpha(image.copy(), pygame.Color(0, 255, 0), 120)
            self.unplaceable = colorize_alpha(
                image.copy(), pygame.Color(255, 0, 0), 120
            )

    def create_cable(self):

        if not self.game_ref.own_turn:
            return

        x, y = self.slot_to_pos()
        if "mouse2" in self.game_ref.keypress:
            if point_inside(self.game_ref.mouse_pos, [x, y], self.size):
                if self.cable == None and self.active == True:
                    self.game_ref.sounds["cable_s"].play()
                    self.cable = Cable(
                        self.game_ref,
                        self.team.color,
                        self.game_ref.GT,
                        dont_freeze=True,
                    )
                    self.cable.generate([x, y], self.game_ref.mouse_pos, 3, 4)
                else:
                    self.cable = None

            else:
                self.cable = None
            # else:
            #
            #     for obj in self.game_ref.render_layers["3.BUILDINGS"]:
            #         if obj.team == self.team.color and point_inside(self.game_ref.mouse_pos, obj.slot_to_pos(), obj.size):
            #             self.cable = None
            #
            #
            #             cable_temp = Cable(self.team.color, self.game_ref.GT)
            #             cable_temp.generate(self.slot_to_pos(), obj.slot_to_pos(), 45,3)
            #             self.static_cables.append(cable_temp)
            #             print("Created static cable")
            #             break

    def tick_cable(self):
        existing = False
        if self.cable != None:
            self.cable.startpoint.pos = np.array(self.slot_to_pos_c_cam())
            self.cable.endpoint.pos = np.array(self.game_ref.mouse_pos)



            for obj in self.game_ref.render_layers["3.BUILDINGS"]:
                if (
                    obj != self
                    and obj.team == self.team
                    and point_inside(
                        self.game_ref.mouse_pos, obj.slot_to_pos(), obj.size
                    )
                ):
                    x, y = obj.slot_to_pos()
                    if self.game_ref.check_cable_availablity(self, obj):
                        existing = self.game_ref.cable_exists(self, obj)
                        if existing:


                            pygame.draw.rect(
                                self.game_ref.screen,
                                [255, 0, 0],
                                [x, y, obj.size[0], obj.size[1]],
                                5,
                            )

                            if "mouse2" not in self.game_ref.keypress_held_down:

                                self.game_ref.render_layers["5.CABLE"].remove(existing)
                                self.cable = None
                                self.game_ref.sounds["cable_e"].play()

                                self.game_ref.datagatherer.data.append(
                                    f"self.game_ref.cut_cable({existing.id})"
                                )

                                self.game_ref.scan_connecting_cables()

                        else:

                            pygame.draw.rect(
                                self.game_ref.screen,
                                [0, 255, 0],
                                [x, y, obj.size[0], obj.size[1]],
                                5,
                            )
                            self.cable.endpoint.pos = np.array(obj.slot_to_pos_c_cam())

                            if "mouse2" not in self.game_ref.keypress_held_down:
                                self.cable = None
                                self.game_ref.sounds["cable_e"].play()

                                cable_temp = Cable(
                                    self.game_ref, self.team.color, self.game_ref.GT
                                )
                                cable_temp.generate(
                                    self.slot_to_pos_c_cam(),
                                    obj.slot_to_pos_c_cam(),
                                    0,
                                    3,
                                    start_obj=self,
                                    end_obj=obj,
                                )

                                self.game_ref.datagatherer.data.append(
                                    f'self.game_ref.render_layers["5.CABLE"].append(Cable(self.game_ref, {self.team.color}, self.game_ref.GT).generate(self.game_ref.find_object_id({self.id}).slot_to_pos_c_cam(),self.game_ref.find_object_id({obj.id}).slot_to_pos_c_cam(),0, 3, start_obj = self.game_ref.find_object_id({self.id}), end_obj = self.game_ref.find_object_id({obj.id}), id = {cable_temp.id}))'
                                )

                                #

                                self.game_ref.render_layers["5.CABLE"].append(
                                    cable_temp
                                )
                                self.game_ref.scan_connecting_cables()
                                print("Created static cable")
                                break
                    else:
                        pygame.draw.rect(
                            self.game_ref.screen,
                            [255, 0, 0],
                            [x, y, obj.size[0], obj.size[1]],
                            5,
                        )
                    break

            if "mouse2" not in self.game_ref.keypress_held_down:
                if self.cable:
                    self.game_ref.sounds["cable_c"].play()
                self.cable = None

            if self.cable != None:
                if existing:
                    existing.tick(color_override=[255, 0, 0], ignore_camera=True)
                else:
                    self.cable.tick()
            try:
                self.dist = round(
                    core.func.get_dist_points(
                        self.cable.startpoint.pos, self.cable.endpoint.pos
                    )
                )

                text = f"{self.dist}/500 u." if not existing else "CUT"



                core.func.render_text(
                    self.game_ref,
                    text,
                    core.func.minus(self.cable.endpoint.pos, [20, -20]),
                    20,
                    color=self.team.color
                    if self.dist < 500 and text != "CUT"
                    else [255, 0, 0],
                )
            except:
                pass

    def render_buildable(self, occ_slots):
        unplaceable = False
        for x_1 in range(self.slot_size[0]):
            for y_1 in range(self.slot_size[1]):

                if self.requirement != None:
                    if self.slot not in self.requirement:
                        unplaceable = True

                if [
                    self.slot[0] + x_1,
                    self.slot[1] + y_1,
                ] in occ_slots or not self.game_ref.slot_inside(self.slot):
                    unplaceable = True
        if not unplaceable:
            if not self.check_los():
                unplaceable = True

        x, y = self.slot_to_pos()
        if unplaceable:
            pygame.draw.rect(
                self.game_ref.screen,
                [255, 0, 0],
                [x + 5, y + 5, self.size[0] - 10, self.size[1] - 10],
                4,
            )
            self.game_ref.screen.blit(self.unplaceable, [x, y])
            self.able_to_place = False
        else:
            pygame.draw.rect(
                self.game_ref.screen,
                [0, 255, 0],
                [x + 5, y + 5, self.size[0] - 10, self.size[1] - 10],
                4,
            )
            self.game_ref.screen.blit(self.placeable, [x, y])
            self.able_to_place = True

    def render_buildable_energy_well(self, occ_slots):
        x, y = self.slot_to_pos()
        if self.slot not in occ_slots:
            pygame.draw.rect(
                self.game_ref.screen,
                [0, 255, 0],
                [x + 5, y + 5, self.size[0] - 10, self.size[1] - 10],
                4,
            )
            self.game_ref.screen.blit(self.placeable, [x, y])
            self.able_to_place = True

        else:
            pygame.draw.rect(
                self.game_ref.screen,
                [255, 0, 0],
                [x + 5, y + 5, self.size[0] - 10, self.size[1] - 10],
                4,
            )
            self.game_ref.screen.blit(self.unplaceable, [x, y])
            self.able_to_place = False

    def tick_buildable(self, occ_slots):
        self.slot = self.pos_to_slot(self.game_ref.get_pos_rev(self.game_ref.mouse_pos))
        # if self.name == "Energy Well":
        #     self.render_buildable_energy_well(occ_slots)
        # else:
        self.render_buildable(occ_slots)

    def get_resource(self):
        if (
            self.name != "Mining Station"
            or self.resource != ""
            or not self.connected_building()
        ):
            return
        self.resource = [
            x
            for x in self.game_ref.render_layers["1.BOTTOM"]
            if x.type == "mine" and x.slot == self.slot
        ][0].resource
        print(self.resource)
        if self.resource == "Iridium":
            self.game_ref.datagatherer.data.append(
                f"self.game_ref.set_notification('{self.resource} found by {self.game_ref.player_team.name}!', color = {self.game_ref.player_team.color})"
            )
            self.game_ref.set_notification(
                "Iridium found!", color=self.game_ref.player_team.color
            )

    def tick_animation(self):
        if self.top_layer:
            x1, y1 = self.slot_to_pos()
            if self.connected_building():
                self.animate_tick.tick()
            posx = (self.move_between[1][0] - self.move_between[0][0]) / 2 + math.sin(
                math.pi * 2 * self.animate_tick.value / self.animate_tick.max_value
            ) * (self.move_between[1][0] - self.move_between[0][0]) / 2
            posy = (self.move_between[1][1] - self.move_between[0][1]) / 2 + math.sin(
                math.pi * 2 * self.animate_tick.value / self.animate_tick.max_value
            ) * (self.move_between[1][1] - self.move_between[0][1]) / 2
            self.game_ref.screen.blit(self.top_layer, [x1 + posx, y1 + posy])

    def cable_send(self):
        if self.name == "Base":
            if self.cable_send_tick.tick():
                for x in self.connected_cables:
                    if x.parent_cable.start_obj.disabled_for_turns == 0 and x.parent_cable.end_obj.disabled_for_turns == 0:
                        x.i = 30
                # if self.own():
                #     self.game_ref.play_sound("base_beep")

    def tick(self):
        self.los()
        if hasattr(self, "resource"):
            self.get_resource()

        self.click()
        self.activation_smoothing()

        if self.active:
            if "esc" in self.game_ref.keypress:
                self.activate(False)

        self.render(self)
        self.cable_send()
        self.tick_buttons()
        self.tick_queue()
        self.tick_cable()
        self.create_cable()
        self.create_spark()
        self.tick_animation()
        self.tick_statuses()
        self.delete()
