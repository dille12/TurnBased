import core.image_transform
import core.func
import pygame


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
    ):
        self.x = slotx
        self.y = sloty
        self.game_ref = game
        self.parent_ref = obj
        self.team = team
        self.image = image
        self.image2 = core.image_transform.colorize_alpha(
            image.copy(), pygame.Color(0, 0, 0), 100
        )
        self.active = False
        self.oneshot = oneshot
        self.oneshot_func = oneshot_func
        self.active = active
        self.argument = argument
        self.activator = activator
        self.key_press = key_press
        self.button_sizex, self.button_sizey = self.image.get_size()

    def tick(self):

        inside = core.func.point_inside(
            self.game_ref.mouse_pos,
            [self.x * 100 * self.game_ref.qsc, self.y * 100 * self.game_ref.qsc],
            [
                self.button_sizex * self.game_ref.qsc,
                self.button_sizey * self.game_ref.qsc,
            ],
        )

        if inside and self.argument != None and not isinstance(self.argument, str):
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

        if (
            inside and "mouse0" in self.game_ref.keypress
        ) or self.key_press in self.game_ref.keypress:
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
