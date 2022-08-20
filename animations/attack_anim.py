
from game_objects.particles.shootparticles import ShootParticle
import math
import random
class AttackAnimation:
    def __init__(self, attacker, defender, damage = 50):
        self.game_ref = attacker.game_ref
        self.pos = attacker.slot_to_pos_center()
        self.pos2 = defender.slot_to_pos_center()
        self.anim_tick = self.game_ref.GT(60, oneshot = True)
        self.game_ref.animations.append(self)
        self.stages = {20 : self.gen_particles, 40 : self.damage_defender}
        self.damage = damage
        self.attacker = attacker
        self.defender = defender


    def tick(self):
        if not self.anim_tick.tick():
            del_stages = []
            for x in self.stages:
                if self.anim_tick.value > x:
                    self.stages[x]()
                    del_stages.append(x)
            for x in del_stages:
                del self.stages[x]
        else:
            self.game_ref.animations.remove(self)


    def gen_particles(self):
        self.game_ref.vibration = 20
        angle = math.atan2(self.pos2[1] - self.pos[1], self.pos2[0] - self.pos[0])
        for i in range(40):
            velx, vely = [
                random.randint(10,40) * math.cos(angle+random.uniform(-0.1, 0.1)),
                random.randint(10,40) * math.sin(angle+random.uniform(-0.1, 0.1))
            ]
            self.game_ref.render_layers["PARTICLES"].append(
                ShootParticle(self.game_ref, self.pos, [velx, vely])
            )

    def damage_defender(self):

        self.defender.hp_change(self.damage)
        for i in range(30):
            self.defender.create_spark(force = True)
