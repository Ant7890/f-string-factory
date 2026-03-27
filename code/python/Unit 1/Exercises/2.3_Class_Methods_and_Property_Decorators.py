"""
2.3 Class Methods and Property Decorators

Use vehicle5.py and dealership.py as a model to complete this

Goal: Modify the existing class from the previous exercise to include a class attribute/method and a property decorator

STEP-BY-STEP:
    STEP 1 - Add a property decorator
        Choose one attribute, it could be the one you wrote a getter/setter method for previously or another one.
        Write a property decorator for it that allows you to return its value
            See the @property in vehicle5.py for an example

    STEP 2 - Add a setter decorator
        Use the property decorator you wrote in STEP 1 to create a setter decorator.
        The decorator should accept at least one parameter similar to the setter method you wrote previously.
        The decorator should validate some data or condition, then set a new value or reject the request with a message.
        See the @price.setter decorator in vehicle5.py for an example

    STEP 3 - Demonstrate the use of your decorators.
        Create an instance from your class.
        Use the property decorator to display an attribute.
            For example, we used car1.price in vehicle5.py

        Use the setter decorator to:
            1) Set a value that will be accepted and set,
                For example, we used car1.price = 35000 in vehicle5.py
            2) Set another value that will be rejected

    STEP 4 - Create a class attribute
        Create an attribute that will be applied to every instance created from the class. It DOES NOT have to be private or protected.
            For example, we used __CAR_COUNT = 0 in vehicle5.py

    STEP 5 - Create a class method
        Create a class method decorator that will apply to every instance from a class in the same way.
        Call the class method from your constructor (__init__) when the object is created,
            For example, we created:
                    @classmethod
                    def increase_car_count(cls)
                Then called it using: Car.increase_car_count()

    STEP 6 - Demonstrate that your class attribute works by calling it from your main code,
        For example, we used:
            print(Car._Car__CAR_COUNT)
        ...to show that the car count goes up after every car instance is created
"""

import random


class Warrior():
    # STEP 4 - Class attribute: tracks total number of Warrior instances created
    __WARRIOR_COUNT = 0

    # STEP 5 - Class method: increments the count each time a new Warrior is created
    @classmethod
    def increase_warrior_count(cls):
        cls.__WARRIOR_COUNT += 1

    def __init__(self, name, clan, health=100, level=1, xp=0, coins=0, maxweight=150, is_alive=True):
        Warrior.increase_warrior_count()  # STEP 5 - Called on every new instance

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


keith = Warrior(name="Keith", clan="Scary Larry Gang", health=80, xp=45)

print(keith.xp)

keith.xp = 200
keith.xp = -50

bronn = Warrior(name="Bronn", clan="Scary Larry Gang")
tormund = Warrior(name="Tormund", clan="Free Folk")

print(Warrior._Warrior__WARRIOR_COUNT)  # Output: 3
