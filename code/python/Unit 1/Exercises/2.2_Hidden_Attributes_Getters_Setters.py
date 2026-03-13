"""
2.2 - Hidden Attributes and Getters/Setters

Goal: You will modify your existing class from previous lessons.

STEP-BY-STEP:
    STEP 1 — Add a Protected Attribute
        Choose one attribute that the object should not be changed directly by outside code (but can still be read if needed).
        Add it using one underscore:
            For example:
                self._protected_value = 10

    STEP 2 - Add a Private Attribute
        Choose another attribute that should be fully hidden from users, because it affects internal logic.
            Add it using two underscores:
            For example:
                self.__private_value = 100

    STEP 3 - Write a Getter Method (for one of your protected or private methods)

    STEP 4 - Write a Setter Method and include a validation check before the return (for one of your protected or private methods)

    STEP 5 — Demonstrate Your Getter and Setter Methods

        After you finish the class:
        - Create an object
        - Try printing the protected attribute
        - Use your getter to read the private attribute
        - Use your setter to change the private attribute
        - Print the private value again to confirm it changed
"""

import random

class Warrior():
    def __init__(self, name, clan, health=100, level=1, xp=0, coins=0, maxweight=150, is_alive=True):
        self.name = name
        self.clan = clan
        self._health = health
        self.level = level
        self.__xp = xp
        self.coins = coins
        self.max_weight = maxweight
        self.inventory = []
        self.is_alive = is_alive

    def get_health(self):
        return self._health

    def get_xp(self):
        return self.__xp

    def set_xp(self, amount):
        if not isinstance(amount, int) or amount < 0:
            return f"Invalid XP value."
        self.__xp = amount
        return f"{self.name}'s XP set to {self.__xp}."

    def attack(self, target):
        damage = random.randint(10, 25)
        self.__xp += 10
        return target.take_damage(damage)

    def take_damage(self, amount):
        self._health -= amount
        if self._health <= 0:
            self._health = 0
            self.is_alive = False
            return f"{self.name} has fallen in battle!"
        return f"{self.name} took {amount} damage and now has {self._health} HP."

    def heal(self, amount):
        if not self.is_alive:
            return f"{self.name} cannot be healed - they have already fallen."
        self._health = min(100, self._health + amount)
        return f"{self.name} healed {amount} HP and now has {self._health} HP."

    def defend(self, block_amount):
        self._health = min(100, self._health + block_amount)
        return f"{self.name} blocks! Absorbed {block_amount} damage, now at {self._health} HP."

    def level_up(self):
        xp_needed = self.level * 50
        if self.__xp >= xp_needed:
            self.__xp -= xp_needed
            self.level += 1
            self.max_weight += 25
            return f"{self.name} reached Level {self.level}!"
        return f"{self.name} needs {xp_needed - self.__xp} more XP to level up."

    def current_weight(self):
        return sum(i["weight"] for i in self.inventory)

    def add_item(self, item):
        if self.current_weight() + item["weight"] > self.max_weight:
            return f"Can't carry '{item['name']}' — too heavy!"
        self.inventory.append(item)
        return f"'{item['name']}' added to {self.name} inventory."

keith = Warrior(name="Keith", clan="Scary Larry Gang", health=80, xp=45)

print(keith.get_health())
print(keith.get_xp())
print(keith.set_xp(200))
print(keith.get_xp())
print(keith.set_xp(-10))