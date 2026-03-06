"""
Exercise 2.1 - Implementing Methods

Goal: Implement at least TWO methods in the class you previously designed in the previous exercises.

STEP-BY-STEP:
    STEP 1 — Choose AT LEAST TWO Methods You Wrote Earlier and Implement It (you can do more)
        Your method MUST:
            Receive at least one parameter (besides self)
            Modify at least one attribute
            return a message or result

            For example:
                If your class was a GameCharacter a simple method could:
                    def take_damage(self, amount):
                        self.health -= amount
                        return f"{self.name} now has {self.health} HP."

    STEP 2 — Create an instance of the object and Call Your Methods separately

    STEP 3 — Test Your Methods Thoroughly
        Write at least three test cases - for example:

            obj = MyClass("A", "B", "C", 10)
            print(obj.take_damage(5))
            print(obj.take_damage(10))
            print(obj.take_damage(3))
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
        damage = random.randint(10, 25)
        self.xp += 10
        target.health -= damage
        if target.health <= 0:
            target.health = 0
            target.is_alive = False
            return f"{target.name} has been slain!"
        return f"{self.name} attacks {target.name} for {damage} damage! {target.name} has {target.health} HP left."

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            return f"{self.name} has fallen in battle!"
        return f"{self.name} took {amount} damage and now has {self.health} HP."

    def heal(self, amount):
        if not self.is_alive:
            return f"{self.name} cannot be healed - they have already fallen."
        self.health = min(100, self.health + amount)
        return f"{self.name} healed {amount} HP and now has {self.health} HP."

    def defend(self, block_amount):
        self.health = min(100, self.health + block_amount)
        return f"{self.name} blocks! Absorbed {block_amount} damage, now at {self.health} HP."

    def level_up(self):
        xp_needed = self.level * 50
        if self.xp >= xp_needed:
            self.xp -= xp_needed
            self.level += 1
            self.max_weight += 25
            return f"{self.name} reached Level {self.level}!"
        return f"{self.name} needs {xp_needed - self.xp} more XP to level up."

    def current_weight(self):
        return sum(i["weight"] for i in self.inventory)

    def add_item(self, item):
        current_weight = sum(i["weight"] for i in self.inventory)
        if current_weight + item["weight"] > self.max_weight:
            return f"Can't carry '{item['name']}' — too heavy!"
        self.inventory.append(item)
        return f"'{item['name']}' added to {self.name} inventory."

keith = Warrior(
    name="Keith",
    clan="Scarry Larry Gang",
    health=99,
    level=47,
    xp=9999,
    coins=3, #He spent it all on cool cat posters
    maxweight=999,
    is_alive=True
)

keith.inventory = [{"name": "Crumpled IOU from Scary Larry","weight": 0}]

print(f"{keith.name} of the {keith.clan} was looking at his recently acquired item from his boss, 1x: '{keith.inventory[0]['name']}'")
print(f"While he was managing his inventory someone attacked!")
print(keith.take_damage(10))
print(keith.take_damage(30))
print(keith.take_damage(5))
print("\nOww, That hurt!")
print(keith.heal(20))
print(keith.heal(100))
print(keith.heal(5))
print(f"{keith.name} was already in his inventory and drank some of his potions.")
print(f"\n{keith.name} conveniently found some items that may be of great use to him!")
print(keith.add_item({"name": "Ancestral Claymore (bent)", "weight": 120}))
print(keith.current_weight())
print(keith.add_item({"name": "A Live Raccoon", "weight": 15}))
print(keith.current_weight())
print("\n")

print(f"Darn! {keith.name} was jumped out of nowhere, he prepared to fight but the attacker was already gone!")

scary_larry = Warrior(
    name="Scary Larry",
    clan="Scary Larry Gang",
    health=100,
    level=99,
    xp=999999,
    coins=0,        # never needed money
    maxweight=9999,
    is_alive=True
)

scary_larry.inventory = [{"name": "Fists of steel", "weight": 0}]

gerald = Warrior(
    name="Gerald",
    clan="None (he's an accountant)",
    health=100,
    level=1,
    xp=0,
    coins=340,      # has exact change for everything
    maxweight=150,
    is_alive=True
)

gerald.inventory = [
    {"name": "Mechanical Pencil", "weight": 0},
    {"name": "Half a Granola Bar", "weight": 0},
]

print(f"{scary_larry.name} seen the whole thing, he gave {keith.name} an IOU a while ago, but he doesn't like owing anyone.")
print(f"{gerald.name} has wandered into the wrong part of town.\n")

print(scary_larry.attack(gerald))
print(scary_larry.attack(gerald))
print(scary_larry.attack(gerald))
print(scary_larry.attack(gerald))
print(scary_larry.attack(gerald))

if not gerald.is_alive:
    print(f"\nGerald never stood a chance. He knew it too.")
else:
    print(f"\nGerald was able to live another day, but perhaps the lesson stuck with him.")

print(f"{scary_larry.name} has paid his debt to {keith.name}, he must go tell him.")