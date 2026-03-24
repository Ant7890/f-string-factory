"""
2.4 Inheritance

Goal: Extend your previous class by creating another class that is a child class of the current one

STEP-BY_STEP:
    STEP 1: Think of an IS-A relationship that could apply to your current class to form a child class.
        For example: If you have a class called 'warrior' maybe a child class could be 'Samurai'

    STEP 2: Write a new class that inherits from your old class
        Add AT LEAST one attribute in your child class that your parent class does not have
        Remember to properly initialize the child class and include super() to initialize the attributes in the parent class
            See the vehicle6.py example of how we did this

    STEP 3: Write a new method in your child class
        The new method SHOULD be named the same as in your parent class but do something different

            For example, if you have a method called attack in your parent class it should also be in your child class.
                However, the two methods should NOT be identical

    STEP 4: Demonstrate your implementation by creating an instance from the child class and calling the method
"""

import random

class Warrior():
    __WARRIOR_COUNT = 0

    @classmethod
    def increase_warrior_count(cls):
        cls.__WARRIOR_COUNT += 1

    def __init__(self, name, clan, health=100, level=1, xp=0, coins=0, maxweight=150, is_alive=True):
        Warrior.increase_warrior_count()

        self.name = name
        self.clan = clan
        self._health = health
        self.level = level
        self.__xp = xp
        self.coins = coins
        self.max_weight = maxweight
        self.inventory = []
        self.is_alive = is_alive

    @property
    def xp(self):
        return self.__xp

    @xp.setter
    def xp(self, amount):
        if not isinstance(amount, int) or amount < 0:
            print(f"Invalid XP value: must be a non-negative integer.")
        else:
            self.__xp = amount
            print(f"{self.name}'s XP set to {self.__xp}.")

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

class Berserker(Warrior):
    def __init__(self, name, clan, health=120, level=1, xp=0, coins=0, maxweight=200, is_alive=True, rage=0):
        super().__init__(name, clan, health, level, xp, coins, maxweight, is_alive)
        self.rage = rage

    def take_damage(self, amount):
        self.rage += amount // 10  # getting hit makes him angrier
        return super().take_damage(amount)

    def attack(self, target):
        base_damage = random.randint(10, 25)
        rage_bonus = self.rage * 2
        total_damage = base_damage + rage_bonus
        self.rage = 0
        return f"{self.name} attacks for {total_damage} damage ({base_damage} base + {rage_bonus} rage bonus)!\n" + target.take_damage(total_damage)

scary_larry = Berserker(name="Scary Larry", clan="Scary Larry Gang", health=120)
keith = Warrior(name="Keith", clan="Scary Larry Gang", health=100)

print(f"{scary_larry.name} enters the battlefield with {scary_larry._health} HP and {scary_larry.rage} rage.\n")

print(keith.attack(scary_larry))
print(keith.attack(scary_larry))
print(f"{scary_larry.name} has built up {scary_larry.rage} rage!\n")

print(scary_larry.attack(keith))
print(f"\n{scary_larry.name} rage after attack: {scary_larry.rage}")