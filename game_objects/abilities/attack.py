from animations.attack_anim import AttackAnimation
def attack(self, obj, argument = 0):
    if self.own():
        self.center()
    elif obj.own():
        obj.center()
    self.game_ref.play_sound("shoot")
    AttackAnimation(self, obj, damage = argument)
    self.shots -= 1


    self.game_ref.vibration = 10
