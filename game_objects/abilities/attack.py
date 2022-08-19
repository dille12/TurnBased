
def attack(self, obj):
    self.shots -= 1
    damage = round(-50 * (self.battery_life/self.battery_life_max))
    obj.hp_change(damage)
    self.game_ref.vibration = 10
