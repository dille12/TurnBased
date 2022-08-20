from core.player import Player

BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
BLUE = [51, 102, 255]
RED = [255, 0, 102]
GREEN = [153, 255, 51]
YELLOW = [255, 204, 102]
CYAN = [51, 204, 204]

ore_colorkeys = {
"Iridium" : [255, 0, 0],
"Uranium" : [0, 255, 0],
"Tungsten" : [51, 204, 255],
"Gallium" : [255, 102, 0],
}

blue_t = Player(BLUE, "", "blue_t")
red_t = Player(RED, "", "red_t")
green_t = Player(GREEN, "", "green_t")
yellow_t = Player(YELLOW, "", "yellow_t")
nature = Player(BLACK, "Nature", "nature")


placeholder = Player(WHITE, "", "placeholder")


class GameTick:
    def __init__(self, max_value=30, oneshot=False):
        self.value = 0
        self.max_value = max_value
        self.oneshot = oneshot

    def tick(self):
        if self.value < self.max_value:
            self.value += 1
        if self.value < self.max_value:
            return False
        else:
            if not self.oneshot:
                self.value = 0
            return True

    def rounded(self):
        return round(self.value)
