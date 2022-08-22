
def shortcircuit(self, target_object, argument):
    if self.own():
        self.center()
    elif target_object.own():
        target_object.center()
    self.shots -= 1
    self.game_ref.vibration = 10
    list_of_objects = self.game_ref.scan_from_building(target_object)
    self.game_ref.sounds["shortcircuit"].play()
    for x in list_of_objects:
        x.disabled_for_turns = 3
        for i in range(20):
            x.create_spark()
