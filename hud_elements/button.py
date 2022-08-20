import core.image_transform
import core.func
import pygame
from values import *


class Button:
    def __init__(
        self,
        game,
        obj,
        slotx,
        sloty,
        team,
        image,
        activator="",
        oneshot=False,
        oneshot_func=None,
        active=False,
        argument=None,
        key_press="",
        scale=False,
        togglable=False,
        executable_function=False
    ):

        self.game_ref = game
        self.x = slotx / self.game_ref.size_conv[0]
        self.y = sloty / self.game_ref.size_conv[1]
        self.parent_ref = obj
        self.exec_func = executable_function
        self.team = team
        if scale:
            self.image = pygame.transform.scale(image.copy(), [100, 100])
        else:
            self.image = image.copy()
        self.image2 = core.image_transform.colorize_alpha(
            self.image.copy(), pygame.Color(0, 0, 0), 100
        )
        self.active = False
        self.oneshot = oneshot
        self.oneshot_func = oneshot_func
        self.active = active
        self.argument = argument
        self.activator = activator
        self.key_press = key_press
        self.button_sizex, self.button_sizey = self.image.get_size()
        self.togglable = togglable

    def tick(self):

        inside = core.func.point_inside(
            self.game_ref.mouse_pos,
            [self.x * 100 * self.game_ref.qsc, self.y * 100 * self.game_ref.qsc],
            [
                self.button_sizex * self.game_ref.qsc,
                self.button_sizey * self.game_ref.qsc,
            ],
        )

        if inside:
            if not isinstance(self.argument, str) and self.argument != None:
                core.func.render_text(
                    self.game_ref,
                    self.argument.name,
                    core.func.minus(self.game_ref.mouse_pos, [100, 50]),
                    40,
                    color=self.team,
                )
                core.func.render_text(
                    self.game_ref,
                    self.argument.desc,
                    core.func.minus(self.game_ref.mouse_pos, [100, 100]),
                    20,
                    color=self.team,
                )
                core.func.render_text(
                    self.game_ref,
                    f"Energy usage: {self.argument.energy_consumption}",
                    core.func.minus(self.game_ref.mouse_pos, [100, 130]),
                    30,
                    color=self.team,
                )
                if hasattr(self.argument, "ore_cost"):
                    y_pos = 160
                    for ore in self.argument.ore_cost:
                        if self.argument.ore_cost[ore] != 0:
                            core.func.render_text(
                                self.game_ref,
                                f"{ore} usage: {self.argument.ore_cost[ore]}",
                                core.func.minus(self.game_ref.mouse_pos, [100, y_pos]),
                                30,
                                color=ore_colorkeys[ore],
                            )
                            y_pos += 30
            elif self.activator != "":
                core.func.render_text(
                    self.game_ref,
                    self.activator,
                    core.func.minus(self.game_ref.mouse_pos, [100, -50]),
                    40,
                    color=self.team,
                )



        if (
            (inside and "mouse0" in self.game_ref.keypress)
            or (self.key_press in self.game_ref.keypress and not self.game_ref.chat.chatbox.active)
        ) and self.game_ref.own_turn:
            self.game_ref.sounds["button"].stop()
            self.game_ref.sounds["button"].play()

            # self.game_ref.sounds["menu1"].play()
            if self.oneshot:
                self.oneshot_func(self.argument)
            else:
                if not self.active:
                    self.active = True

                    if self.parent_ref != None:

                        for x in self.parent_ref.buttons:
                            if x != self:
                                x.active = False
                elif self.togglable:
                    self.active = False

            if self.exec_func:
                self.exec_func(self.active)

            try:
                self.parent_ref.check_mode()
            except:
                pass

        if inside:
            color = [255, 255, 255]
            image = self.image
            width = 5
        else:
            if self.active:
                color = self.team
                image = self.image
                width = 5
            else:
                color = self.team
                image = self.image2
                width = 1
        smoothing = 0
        if self.parent_ref != None:
            smoothing = self.parent_ref.smoothing

        self.game_ref.screen.blit(
            image,
            [
                self.x * 100 * self.game_ref.qsc,
                self.y * 100 * self.game_ref.qsc + smoothing,
            ],
        )
        pygame.draw.rect(
            self.game_ref.screen,
            color,
            [
                self.x * 100 * self.game_ref.qsc,
                self.y * 100 * self.game_ref.qsc + smoothing,
                self.button_sizex * self.game_ref.qsc,
                self.button_sizey * self.game_ref.qsc,
            ],
            width,
        )
        if self.key_press != "":
            core.func.render_text(
                self.game_ref,
                self.key_press.upper(),
                [
                    self.x * 100 * self.game_ref.qsc + 5,
                    self.y * 100 * self.game_ref.qsc + smoothing + 5,
                ],
                20,
                color=color,
            )
