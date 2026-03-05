"""
Exercise 1.2 - Adding Constructor Parameters

 -- Use vehicles2.py from class as an example to help complete this. --

Goal: Extend the class you created in the previous exercise (1.1) by adding parameters to the constructor (__init__)
      so attributes are set when the object is created. Then manipulate the objects you create with the class.

      This mirrors the example:
            def __init__(self, make, model, color, price, sold=False):

STEP-BY-STEP:
    STEP 1 — Modify Your Existing Class
        Take the class you created in the previous lesson and rewrite its __init__ method so it accepts parameters.
        At least ONE of your parameters should have a DEFAULT/KEYWORD VALUE.
            for example -  we used 'sold = False' as a DEFAULT VALUE


    STEP 2 — Create one Object Using Your New Constructor
        Create at least one object of your class using the new parameters. in the main body of your code.

    STEP 3 — Print the Object’s Attributes in a dictionary

    STEP 4 - Create a loop that allows users to generate more objects using a for loop and store to a list
        You can do this using user input like we did in the example program or assigning them static values during the loop

    STEP 5- Write a conditional to check an attribute value of your choice from an object in the list
            You can do this through user input or by choosing an arbitrary element

                In our example, we used the first element and checked its sold attribute using:
                    if cars_dict[0]['sold']
"""

import random

class Warrior():
    def __init__(self, name, clan, health=100, level=1, xp=0, coins=0, maxweight=150, is_alive=True):
        self.name = name
        self.clan = clan
        self.health = health
        self.level = level
        self.xp = xp
        self.coins = coins
        self.max_weight = maxweight
        self.inventory = []
        self.is_alive = is_alive

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


# STEP 2 - Create one object
w1 = Warrior("Keith", "Scary Larry Gang")

# STEP 3 - Print attributes as a dictionary
print(w1.__dict__)

# STEP 4 - Loop with user input to create more objects
warriors_list = []

num_warriors = int(input("How many warriors do you want to create? "))

for i in range(num_warriors):
    name = input("Enter warrior name: ")
    clan = input("Enter warrior clan: ")
    is_alive = random.choice([True, False])
    warriors_list.append(Warrior(name, clan, is_alive=is_alive))

# STEP 5 - Conditional checking an attribute
if warriors_list[0].is_alive:
    print(f"{warriors_list[0].name} is still standing!")
else:
    print(f"{warriors_list[0].name} has fallen.")