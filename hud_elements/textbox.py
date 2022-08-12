import pygame
import pyperclip


class TextBox:
    def __init__(self, game, pos, default, secret=False, size = 20):
        self.pos = pos
        self.game_ref = game
        self.box = pygame.Rect(self.pos[0], self.pos[1], 140, 32)
        self.color_active = pygame.Color([255, 0, 0])
        self.color_inactive = pygame.Color([100, 100, 100])
        self.color = self.color_inactive
        self.font = game.terminal[size]
        self.text = str(default)
        self.active = False
        self.secret = secret

    def tick(self):
        if "mouse0" in self.game_ref.keypress:

            # If the user clicked on the input_box rect.
            if (
                self.box.collidepoint(self.game_ref.mouse_pos)
                or "enter" in self.game_ref.keypress
            ):
                self.game_ref.sounds["button"].play()
                # Toggle the active variable.
                self.active = not self.active
            else:
                if self.active:
                    self.game_ref.sounds["button"].play()

                self.active = False
            # Change the current color of the input box.
            self.color = self.color_active if self.active else self.color_inactive
        if self.active:
            paste_ticks = 0
            if "backspace" in self.game_ref.keypress_held_down:
                self.backspace_tick += 1
                if self.backspace_tick > 30:
                    self.text = self.text[:-1]
            else:
                self.backspace_tick = 0
            for event in self.game_ref.events:
                if event.type == pygame.KEYDOWN and self.active:
                    self.game_ref.play_sound("type")
                    if (
                        pygame.key.get_pressed()[pygame.K_v]
                        and pygame.key.get_pressed()[pygame.K_LCTRL]
                    ):
                        self.text = pyperclip.paste()
                        print("PASTED")
                        break
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    elif "enter" not in self.game_ref.keypress:
                        self.text += event.unicode

        # Render the current text.
        if self.secret:
            txt_surface = self.font.render("*" * len(self.text), True, (255, 255, 255))
        else:
            txt_surface = self.font.render(self.text, True, (255, 255, 255))
        # Resize the box if the text is too long.
        width = max(200, txt_surface.get_width() + 10)
        self.box.w = width
        # Blit the text.
        self.game_ref.screen.blit(txt_surface, (self.pos[0] + 5, self.pos[1] + 5))
        # Blit the input_box rect.
        pygame.draw.rect(self.game_ref.screen, self.color_active if self.active else self.color_inactive, self.box, 2)
