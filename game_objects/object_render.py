import pygame
from values import *
import core.func
def render(self):
    if self.type == "wall":
        return
    if not self.check_los():
        return

    x, y = self.slot_to_pos()

    if self.active:

        smooth_lines_x = self.smoothing_inv * self.slot_size[0] / (3)
        smooth_lines_y = self.smoothing_inv * self.slot_size[1] / (3)

        lines_pos = (1 - self.smooth_value_raw) * 50 + 2

        pygame.draw.line(
            self.game_ref.screen,
            [255, 255, 255],
            [x - lines_pos, y - lines_pos],
            [x - lines_pos + smooth_lines_x, y - lines_pos],
            2,
        )
        pygame.draw.line(
            self.game_ref.screen,
            [255, 255, 255],
            [x - lines_pos, y - lines_pos],
            [x - lines_pos, y - lines_pos + smooth_lines_y],
            2,
        )

        pygame.draw.line(
            self.game_ref.screen,
            [255, 255, 255],
            [
                x + lines_pos + self.size[0] - smooth_lines_x,
                y + lines_pos + self.size[1],
            ],
            [x + lines_pos + self.size[0], y + lines_pos + self.size[1]],
            2,
        )
        pygame.draw.line(
            self.game_ref.screen,
            [255, 255, 255],
            [
                x + lines_pos + self.size[0],
                y + lines_pos + self.size[1] - smooth_lines_y,
            ],
            [x + lines_pos + self.size[0], y + lines_pos + self.size[1]],
            2,
        )

        pygame.draw.rect(
            self.game_ref.screen,
            self.team.color,
            [x + 5, y + 5, self.size[0] - 10, self.size[1] - 10],
            4,
        )
        core.func.render_text(
            self.game_ref,
            self.name,
            [x + self.size[0] / 2, y - 15],
            20,
            centerx=True,
            color=self.team.color,
        )
        core.func.render_text(
            self.game_ref,
            f"HP:{self.hp}",
            [x + self.size[0] / 2, y + self.size[1] + 20],
            20,
            centerx=True,
            color=self.team.color,
        )
    else:
        pygame.draw.rect(
            self.game_ref.screen,
            self.team.color,
            [x + 5, y + 5, self.size[0] - 10, self.size[1] - 10],
            1,
        )
    if self.image != None:
        self.game_ref.screen.blit(self.image, [x, y])

    if hasattr(self, "turn_movement") and self.own():
        for x_1 in range(self.turn_movement):
            pygame.draw.rect(
                self.game_ref.screen,
                self.team.color,
                [
                    x + 5 + 92,
                    y + 5 + x_1 * round(93 / self.movement_range),
                    6,
                    round(93 / self.movement_range) - 10,
                ],
            )

            pygame.draw.rect(
                self.game_ref.screen,
                core.func.mult(self.team.color, 0.5),
                [
                    x + 5 + 92,
                    y + 5 + x_1 * round(93 / self.movement_range),
                    6,
                    round(93 / self.movement_range) - 10,
                ],
                1,
            )

    if hasattr(self, "battery_life") and self.own():
        for x_1 in range(self.battery_life_max):
            if x_1 < self.battery_life:
                pygame.draw.rect(
                    self.game_ref.screen,
                    [0,255,255],
                    [
                        x + 5 + x_1 * round(93 / self.battery_life_max),
                        y + 5 + 92,
                        round(93 / self.battery_life_max) - 2,
                        6,
                    ],
                )

            pygame.draw.rect(
                self.game_ref.screen,
                core.func.mult([0,255,255], 0.5),
                [
                    x + 5 + x_1 * round(93 / self.battery_life_max),
                    y + 5 + 92,
                    round(93 / self.battery_life_max) - 2,
                    6,
                ],
                1,
            )

    if self.team != nature:
        pygame.draw.rect(
            self.game_ref.screen,
            self.team.color,
            [
                x + 5,
                y + 5 + self.size[1],
                round(self.size[0] * 0.95 * self.hp / self.hp_max),
                6,
            ],
        )

        pygame.draw.rect(
            self.game_ref.screen,
            core.func.mult(self.team.color, 0.5),
            [x + 3, y + 3 + self.size[1], round(self.size[0] * 0.95) + 4, 10],
            1,
        )
