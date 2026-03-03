"""
Exercise 1.1 - Create your Own Class

Goal: Practice defining a class, writing an __init__ constructor, creating attributes, and declaring simple method definitions.

Instructions:
    You will design your own class based on an application you choose.
    Examples of themes you may pick include:

        A character in a video game
        A robot in a competition
        A Pokémon-style creature
        A store product
        A spaceship or vehicle
        A pet or animal
        A classroom tool or digital resource

    Choose any idea you like, however, you will expand this idea in the next set of exercies,
        so think about what idea might be interesting to develop as part of a full python program or game.

STEP-BY-STEP:
    STEP 1 — Name Your Class
        Pick a name that represents your object.
            Examples:
                Player, Monster, PetDog, Robot, Spaceship, SoccerBall

        Keep in mind that this name will be the 'template' for creating objects so keep more generic with the name.

    STEP 2 — Define at least 6 attributes
        Your attributes should describe your object.

        They may include:
            strings (name, type, category)
            numbers (health, level, cost, weight, speed)
            booleans (active, alive, unlocked)
            lists (inventory, moves, upgrades)

        Think - what things do you want ALL object for this class to have.
        For example, maybe all spaceships have an attribute called 'fire rate'

    STEP 3 — Define 3–5 method stubs
        A method stub means you write the method name and parameters but leave the body as pass
        Your methods should represent actions your object can perform.

Use the vehicle1.py program as a template for how to approach this
"""

class Warrior():
    def __init__(self, name, clan):
        self.name = name
        self.clan = clan
        self.health = 100
        self.level = 1
        self.xp = 0
        self.coins = 0
        self.max_weight = 150
        self.inventory = []
        self.is_alive = True

    def attack(self, target):
        pass

    def heal(self, amount):
        pass

    def defend(self, block_amount):
        pass

    def level_up(self):
        pass

    def add_item(self, item):
        pass
