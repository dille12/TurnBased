from game_objects.game_object import Game_Object
from game_objects.npc import NPC
from game_objects.building import Building

import pygame
from core.func import *
from core.image_transform import *
from hud_elements.button import *


class Soldier(NPC):
    def __init__(self, game, team, slot):
        hp = 100
        name = "Soldier"
        image = game.images["soldier"].copy()
        movement_range = 3
        self.range = 2
        self.buildtime = 3

        self.energy_generation = 0
        self.energy_consumption = 2

        self.select_sound = game.sounds["select_sold"]

        super().__init__(
            game, team, name, slot, movement_range=movement_range, hp=hp, image=image
        )

        self.buttons = [
            Button(
                self.game_ref,
                self,
                0.5,
                9,
                self.team.color,
                self.game_ref.images["leg"],
                activator="walk",
                active=True,
                key_press="z",
            ),
            Button(
                self.game_ref,
                self,
                2,
                9,
                self.team.color,
                self.game_ref.images["fist"],
                activator="attack",
                key_press="x",
            ),
            Button(
                self.game_ref,
                self,
                3.5,
                9,
                self.team.color,
                self.game_ref.images["shield"],
                activator="defend",
                key_press="c",
            ),
        ]
        self.check_mode()

        self.desc = "Mid-tech battlemech weaponized with dual railguns and armored with a coldfuzed nanocarbon shell."

    def copy(self):
        return Soldier(self.game_ref, self.team, self.slot)


class Saboteur(NPC):
    def __init__(self, game, team, slot):
        hp = 100
        name = "Saboteur"
        image = game.images["saboteur"].copy()
        movement_range = 4
        self.range = 1
        self.buildtime = 3

        self.energy_generation = 0
        self.energy_consumption = 2

        self.select_sound = game.sounds["select_ass"]

        super().__init__(
            game, team, name, slot, movement_range=movement_range, hp=hp, image=image
        )

        self.buttons = [
            Button(
                self.game_ref,
                self,
                0.5,
                9,
                self.team.color,
                self.game_ref.images["leg"],
                activator="walk",
                active=True,
                key_press="z",
            ),
            Button(
                self.game_ref,
                self,
                2,
                9,
                self.team.color,
                self.game_ref.images["fist"],
                activator="attack",
                key_press="x",
            ),
            Button(
                self.game_ref,
                self,
                3.5,
                9,
                self.team.color,
                self.game_ref.images["shortcircuit"],
                activator="sabotage",
                key_press="c",
            ),
        ]

        self.desc = "Sophisticated field stealth attack unit specializing in voluntary circuit shorting."

        self.check_mode()

    def copy(self):
        return Saboteur(self.game_ref, self.team, self.slot)


class Builder(NPC):
    def __init__(self, game, team, slot):
        hp = 50
        name = "Builder"
        image = game.images["builder"].copy()
        movement_range = 2
        self.range = 1
        self.buildtime = 2

        self.energy_generation = 0
        self.energy_consumption = 1

        self.select_sound = game.sounds["select_builder"]

        self.desc = "An old manufacturing unit repurposed for field mass assembly."

        super().__init__(
            game, team, name, slot, movement_range=movement_range, hp=hp, image=image
        )

        self.buttons = [
            Button(
                self.game_ref,
                self,
                0.5,
                9,
                self.team.color,
                self.game_ref.images["leg"],
                activator="walk",
                active=True,
                key_press="z",
            ),
            Button(
                self.game_ref,
                self,
                2,
                9,
                self.team.color,
                self.game_ref.images["fist"],
                activator="attack",
                key_press="x",
            ),
            Button(
                self.game_ref,
                self,
                0.5,
                2,
                self.team.color,
                self.game_ref.images["elec_tower"],
                oneshot=True,
                key_press="1",
                scale=True,
                oneshot_func=self.npc_build,
                argument=ElectricTower(self.game_ref, self.team, [-1, -1]),
            ),
            Button(
                self.game_ref,
                self,
                0.5,
                3.5,
                self.team.color,
                self.game_ref.images["energywell"],
                oneshot=True,
                key_press="2",
                scale=True,
                oneshot_func=self.npc_build,
                argument=EnergyWell(self.game_ref, self.team, [-1, -1]),
            ),
            Button(
                self.game_ref,
                self,
                0.5,
                5,
                self.team.color,
                self.game_ref.images["mining_base"],
                oneshot=True,
                key_press="3",
                scale=True,
                oneshot_func=self.npc_build,
                argument=MiningStation(self.game_ref, self.team, [-1, -1]),
            ),
            Button(
                self.game_ref,
                self,
                0.5,
                6.5,
                self.team.color,
                self.game_ref.images["barracks"],
                oneshot=True,
                key_press="4",
                scale=True,
                oneshot_func=self.npc_build,
                argument=Barracks(self.game_ref, self.team, [-1, -1]),
            ),
            # Button(self.game_ref, self, 3.5,9, self.team.color, self.game_ref.images["shield"], activator = "defend", key_press = "d")
        ]
        self.check_mode()

    def copy(self):
        return Builder(self.game_ref, self.team, self.slot)


class Base(Building):
    def __init__(self, game, team, slot):
        hp = 1000
        name = "Base"

        print("Generating a base to ", slot, team.color, team.name)

        self.select_sound = game.sounds["select_base"]
        self.buildtime = 1
        self.energy_generation = 5
        self.energy_consumption = 0

        image = game.images["base"].copy()
        size = [2, 2]
        self.range = 0
        self.desc = "Base of operations for your team."

        super().__init__(game, team, name, slot, size=size, hp=hp, image=image)
        self.short_circuited = True
        self.buttons = [
            Button(
                self.game_ref,
                self,
                0.5,
                2,
                self.team.color,
                self.game_ref.images["builder"],
                key_press="1",
                oneshot=True,
                oneshot_func=self.purchase,
                argument=Builder(self.game_ref, self.team, [-1, -1]),
            ),
        ]
        if self.team == self.game_ref.player_team:
            print("CENTERING IN START")
            self.center()

    def copy(self):
        return Base(self.game_ref, self.team, self.slot)


class ElectricTower(Building):
    def __init__(self, game, team, slot):
        hp = 200
        name = "Electric Tower"
        image = game.images["elec_tower"].copy()
        self.select_sound = game.sounds["select_2"]
        size = [1, 1]
        self.range = 0
        self.buildtime = 1
        self.energy_generation = 0
        self.energy_consumption = 0
        self.short_circuited = False

        super().__init__(game, team, name, slot, size=size, hp=hp, image=image)

        self.los_rad = 0

        self.desc = "Conduit for electricity."

        self.buttons = [
            Button(
                self.game_ref,
                self,
                0.5,
                9,
                self.team.color,
                self.game_ref.images["circuitbreaker"],
                activator="circuitbreaker",
                active=False,
                key_press="z",
                togglable=True,
                executable_function = self.toggle_circuits
            ),
        ]

    def copy(self):
        return ElectricTower(self.game_ref, self.team, self.slot)


class Barracks(Building):
    def __init__(self, game, team, slot):
        hp = 350
        name = "Barracks"
        image = game.images["barracks"].copy()
        self.select_sound = game.sounds["select_barracks"]
        size = [2, 2]
        self.range = 0
        self.buildtime = 1
        self.energy_generation = 0
        self.energy_consumption = 3

        super().__init__(game, team, name, slot, size=size, hp=hp, image=image)

        self.buttons = [
            Button(
                self.game_ref,
                self,
                0.5,
                2,
                self.team.color,
                self.game_ref.images["soldier"],
                key_press="1",
                oneshot=True,
                oneshot_func=self.purchase,
                argument=Soldier(self.game_ref, self.team, [-1, -1]),
            ),
            Button(
                self.game_ref,
                self,
                0.5,
                3.5,
                self.team.color,
                self.game_ref.images["saboteur"],
                key_press="2",
                oneshot=True,
                oneshot_func=self.purchase,
                argument=Saboteur(self.game_ref, self.team, [-1, -1]),
            ),
            Button(
                self.game_ref,
                self,
                0.5,
                5,
                self.team.color,
                self.game_ref.images["PLACEHOLDER"],
                key_press="3",
                oneshot=True,
                oneshot_func=self.purchase,
                argument=MissileLauncher(self.game_ref, self.team, [-1, -1]),
            ),
        ]

        self.desc = "Produces military units."

    def copy(self):
        return Barracks(self.game_ref, self.team, self.slot)


class EnergyWell(Building):
    def __init__(self, game, team, slot):
        hp = 200
        name = "Energy Well"
        image = game.images["energywell"].copy()
        self.select_sound = game.sounds["select_tower"]
        size = [1, 1]
        self.range = 0
        self.buildtime = 3

        self.energy_generation = 3
        self.energy_consumption = 0

        self.desc = "Harvests energy from deposits."

        super().__init__(game, team, name, slot, size=size, hp=hp, image=image)

        self.requirement = self.game_ref.deposits

    def copy(self):
        return EnergyWell(self.game_ref, self.team, self.slot)


class MiningStation(Building):
    def __init__(self, game, team, slot):
        hp = 200
        name = "Mining Station"
        image = game.images["mining_base"].copy()
        self.select_sound = game.sounds["select_mine"]
        size = [1, 1]
        self.range = 0
        self.buildtime = 3

        self.energy_generation = 0
        self.energy_consumption = 2

        self.desc = "Explores ore deposits and provides access to them."

        super().__init__(game, team, name, slot, size=size, hp=hp, image=image)

        self.requirement = self.game_ref.mine_positions

        self.top_layer = colorize_alpha(
            self.game_ref.images["mining_top"].copy(),
            pygame.Color(self.team.color[0], self.team.color[1], self.team.color[2]),
            50,
        )
        self.move_between = [[0, 0], [0, 50]]
        self.animate_tick = self.game_ref.GT(120)
        self.resource = ""

    def copy(self):
        return MiningStation(self.game_ref, self.team, self.slot)


### TODO ###

class OverclockCenter(Building):
    pass

class SpecialUnitCenter(Building):
    pass

class DockingStation(Building):
    pass

class TransportableBomb(NPC):  ##URANIUM, GALLIUM
    def __init__(self, game, team, slot):
        hp = 50
        name = "Transportable Bomb"
        image = game.images["PLACEHOLDER"].copy()
        self.select_sound = game.sounds["select_tower"]
        size = [1, 1]
        self.range = 0
        self.buildtime = 6
        self.energy_generation = 0
        self.energy_consumption = 4
        self.ore_cost = {"Uranium" : 1, "Gallium" : 1}
        self.desc = "Slow moving atomic bomb on tracks. Upon detonation destroys every tile adjacent to it."
        super().__init__(game, team, name, slot, size=size, hp=hp, image=image)

    def copy(self):
        return TransportableBomb(self.game_ref, self.team, self.slot)

class MissileLauncher(NPC): ### URANIUM
    def __init__(self, game, team, slot):
        hp = 25
        name = "Missile Launcher"
        image = game.images["PLACEHOLDER"].copy()
        self.select_sound = game.sounds["select_tower"]
        size = [1, 1]
        self.range = 0
        self.buildtime = 4
        self.energy_generation = 0
        self.energy_consumption = 3
        movement_range = 2
        self.ore_cost = {"Uranium" : 1}
        self.desc = "Fires small-scale missiles armed with uranium tipped warheads to a detected tile."
        super().__init__(
            game, team, name, slot, movement_range=movement_range, hp=hp, image=image
        )

    def copy(self):
        return MissileLauncher(self.game_ref, self.team, self.slot)
class PhaseCharger(NPC): ### GALLIUM, TUNGSTEN
    def __init__(self, game, team, slot):
        hp = 25
        name = "Phase Charger"
        image = game.images["PLACEHOLDER"].copy()
        self.select_sound = game.sounds["select_tower"]
        size = [1, 1]
        self.range = 0
        self.buildtime = 5
        self.energy_generation = 0
        self.energy_consumption = 5
        self.ore_cost = {"Gallium" : 1, "Tungsten" : 1}

        self.desc = "Can phase through the void to a detected tile."
        super().__init__(game, team, name, slot, size=size, hp=hp, image=image)

    def copy(self):
        return PhaseCharger(self.game_ref, self.team, self.slot)

class CombatMech(NPC): ### TUNGSTEN
    def __init__(self, game, team, slot):
        hp = 250
        name = "Combat Mech"
        image = game.images["PLACEHOLDER"].copy()
        self.select_sound = game.sounds["select_tower"]
        size = [1, 1]
        self.range = 0
        self.buildtime = 3
        self.energy_generation = 0
        self.energy_consumption = 4
        self.ore_cost = {"Tungsten" : 1}

        self.desc = "Slow moving mech engineered to combat situations."
        super().__init__(game, team, name, slot, size=size, hp=hp, image=image)

    def copy(self):
        return CombatMech(self.game_ref, self.team, self.slot)

class Interceptor(NPC): ### GALLIUM
    def __init__(self, game, team, slot):
        hp = 25
        name = "Interceptor"
        image = game.images["PLACEHOLDER"].copy()
        self.select_sound = game.sounds["select_tower"]
        size = [1, 1]
        self.range = 0
        self.buildtime = 3
        self.energy_generation = 0
        self.energy_consumption = 5
        self.ore_cost = {"Gallium" : 1}
        self.desc = "Flying unit ignoring all moving limitations."
        super().__init__(game, team, name, slot, size=size, hp=hp, image=image)

    def copy(self):
        return Interceptor(self.game_ref, self.team, self.slot)

class FissileCannon(NPC): ##TUNGSTEN, URANIUM
    def __init__(self, game, team, slot):
        hp = 25
        name = "Fissile Cannon"
        image = game.images["PLACEHOLDER"].copy()
        self.select_sound = game.sounds["select_tower"]
        size = [1, 1]
        self.range = 0
        self.buildtime = 3
        self.energy_generation = 0
        self.energy_consumption = 5
        self.ore_cost = {"Tungsten" : 1, "Uranium" : 1}
        self.desc = "Fires devastating enriched uranium propelled projectiles."
        super().__init__(game, team, name, slot, size=size, hp=hp, image=image)

    def copy(self):
        return FissileCannon(self.game_ref, self.team, self.slot)

class Railgunner(NPC): ### TUNGSTEN, URANIUM, GALLIUM

    def __init__(self, game, team, slot):
        hp = 25
        name = "Railgunner"
        image = game.images["PLACEHOLDER"].copy()
        self.select_sound = game.sounds["select_tower"]
        size = [1, 1]
        self.range = 0
        self.buildtime = 3
        self.energy_generation = 0
        self.energy_consumption = 5
        self.ore_cost = {"Tungsten" : 1, "Uranium" : 1, "Gallium" : 1}
        self.desc = "Fires tungstenhardened projectiles by propelling them with electromagnetism."
        super().__init__(game, team, name, slot, size=size, hp=hp, image=image)

    def copy(self):
        return FissileCannon(self.game_ref, self.team, self.slot)
