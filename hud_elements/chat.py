import time
import pygame

class Chat:
    def __init__(self, game):
        self.chat = {}
        self.game_ref = game


    def append(self, chat):
        self.chat[time.time()] = chat



    def tick(self):
        y_pos = 20
        for time_1 in sorted(self.chat, reverse = True):
            chat = self.chat[time_1]
            text = self.game_ref.terminal[20].render(str(chat), False, [255,255,255])
            self.game_ref.screen.blit(text, [self.game_ref.resolution[0] - text.get_size()[0], y_pos])
            y_pos += 30

            if time_1 + 5 < time.time() and time_1 in self.chat:
                del self.chat[time_1]
