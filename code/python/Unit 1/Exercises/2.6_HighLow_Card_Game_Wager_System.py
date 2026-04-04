"""
Higher or Lower Card Game
------------------------

This program implements a simple command-line card game using object-oriented programming.

Overview:
    The player starts with a set number of credits and is shown a card from a shuffled deck.
    They must guess whether the next card will be higher or lower in value. If the guess is
    correct, the player wins credits; otherwise, they lose credits. The game continues until
    the player runs out of credits or the deck is empty.

Classes used:
    Card:
        Represents a single playing card.
        Stores rank (e.g., Ace, King), suit (e.g., Hearts), and value (numeric).
        Cards can be concealed or revealed, which controls how they are displayed.

    Deck:
        Manages a collection of Card objects.
        Creates a full deck based on a rank-value dictionary.
        Supports shuffling, drawing cards, and returning cards to the deck.
        Maintains two lists:
            - startingDeckList: the original ordered deck
            - playingDeckList: the active shuffled deck used during gameplay

    Game:
        Controls the overall game logic.
        Handles player credits, betting, user input, and win/loss conditions.
        Uses the Deck class to draw and compare cards.

Key Concepts Demonstrated:
    - Classes and objects
    - Constructors (__init__)
    - Magic methods (__str__)
    - Encapsulation (methods controlling state like reveal/conceal)
    - Composition (Game "has a" Deck, Deck "has many" Cards)
    - Input validation and control flow

How to Run:
    Run the script and follow the prompts in the terminal.
    Enter a bet and guess whether the next card will be higher (h) or lower (l).

Note:
    The `window` parameter in the Card and Deck classes is reserved for potential
    future GUI integration but is not used in this version of the program.
"""

import random

class Card:
    def __init__(self, window, rank, suit, value):
        """
        This defines the Card class, which represents a single card in the deck with its rank, suit, and value.

        The `window` parameter can be used for GUI integration later
        """
        self.rank = rank
        self.suit = suit
        self.value = value
        self.window = window

        self.is_concealed = True


    def __str__(self):
        """
        Returns the card object (i.e. Ace of Hearts) if card not concealed or a message saying such if it is
        """
        if not self.is_concealed:
            return f"{self.rank} of {self.suit}"
        else:
            return "Card is concealed"

    def reveal(self):
        # This method reveals the card by setting `is_concealed` to False.
        self.is_concealed = False

    def conceal(self):
        # This method conceals the card by setting `is_concealed` to True.
        self.is_concealed = True


class Deck:
    """
    This class generates a deck of cards by calling the card object.

    We have the ability to generate multiple decks by passing in values used (i.e. we only use cards higher than 6 for certain games)
    """

    # These are class variables that apply to any deck object generated from this class
    SUIT_TUPLE = ('Diamonds', 'Clubs', 'Hearts', 'Spades')
    STANDARD_DECK = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5,
                     '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                     'J': 11, 'Q': 12, 'K': 13}


    def __init__(self, window, deck_type = STANDARD_DECK):
        # The constructor initializes the deck by creating cards for each suit and rank using the given rank-value dictionary.
        self.startingDeckList = [] # The startingDeckList holds the original unshuffled deck, which allows resetting the deck if needed.
        self.playingDeckList = []  # The playingDeckList is the active deck used during gameplay, which can be shuffled and modified.

        # Generate the deck by calling the card object for each rank and value in the class variable list
        for suit in Deck.SUIT_TUPLE:
            for rank, value in deck_type.items():
                oCard = Card(window, rank, suit, value)
                self.startingDeckList.append(oCard)

        self.shuffle() # call a method to separate playing deck from starting decks and shuffle the generated deck

    def shuffle(self):
        # This method shuffles the deck and ensures all cards are concealed before shuffling.
        self.playingDeckList = self.startingDeckList.copy() # Copy the deck list
        for oCard in self.playingDeckList:
            oCard.conceal()
        random.shuffle(self.playingDeckList)


    def get_card(self):
        # This method removes and returns the top card from the playing deck. Raises an error if no cards are left.
        if len(self.playingDeckList) == 0:
            raise IndexError("No more cards")
        return self.playingDeckList.pop()


    def return_card_to_deck(self, oCard):
        # This method adds a card back to the top of the playing deck.
        self.playingDeckList.append(oCard)


class Game:
    def __init__(self):
        # The Game class handles the game logic, including initializing the deck and managing the score.

        self.deck = Deck(False)  # Pass "None" for window as we are not using GUI
        self.credits = 100  # Starting credits for the player
        self.current_card = self.deck.get_card()
        self.current_card.reveal()

    def calculate_card_multiplier(self, card, guess):
        edge_distance = abs(card.value - 7) / 6 # I looked this up.

        going_higher = (guess == 'h')
        card_leans_high = (card.value - 7)
        card_leans_low = (card.value - 7)

        if (going_higher and card_leans_high) or (not going_higher and card_leans_low):
            direction_risk = 1.0 - edge_distance
        else:
            direction_risk = edge_distance

        return round(1.0 + (direction_risk * 2.0), 2)

    def calculate_bet_bonus(self, bet):
        return round((bet / self.credits), 2)

    def calculate_final_multiplier(self, card, guess, bet):
        return round(self.calculate_card_multiplier(card, guess) + self.calculate_bet_bonus(bet), 2)

    def print_cards(self, left_card, right_card=None):
        suits = {'Diamonds': '♦', 'Clubs': '♣', 'Hearts': '♥', 'Spades': '♠'}

        def card_rows(card):   # I thought this was a good addition, I took some ideas from "https://codereview.stackexchange.com/questions/82103/ascii-fication-of-playing-cards"
            rank = card.rank[:2]
            suit = suits[card.suit]
            return [
                "┌───────────┐",
                f"│ {rank.ljust(2)}        │",
                "│           │",
                f"│     {suit}     │",
                "│           │",
                f"│       {rank.rjust(2)}  │",
                "└───────────┘",
            ]

        hidden_rows = [
            "┌───────────┐",
            "│░░░░░░░░░░░│",
            "│░░░░░░░░░░░│",
            "│░░░░░░░░░░░│",
            "│░░░░░░░░░░░│",
            "│░░░░░░░░░░░│",
            "└───────────┘",
        ]

        left = card_rows(left_card)
        right = card_rows(right_card) if right_card else hidden_rows

        for l, r in zip(left, right):
            print(f"{l}  {r}")

    def get_bet(self):
        while True:
            try:
                bet = int(input("How many credits do you want to bet? ")) #I kept getting the same cards; as soon as I added this and the code to deal with them in the game, they stopped lol.
                if bet == -1:
                    print(f"DEBUG: Next card is {self.deck.playingDeckList[-1]}")
                    self.deck.playingDeckList[-1].reveal()
                    print(f"DEBUG: Next card is {self.deck.playingDeckList[-1]}")
                    self.deck.playingDeckList[-1].conceal()
                    continue
                if 1 <= bet <= self.credits:
                    return bet
                else:
                    print("Invalid bet please enter a number between 1 and your credits")
            except ValueError:
                print("Please enter a valid bet")

    def start_game(self):
        """
        This method runs the game logic during the game.
        It manages checking if there is enough cards, revealing cards, checking bets, calculating credits, and ending the game.
        """
        print("Welcome to the Higher or Lower Card Game!")

        while True:
            if not self.deck.playingDeckList:
                print("No more cards, Game Over!")
                break

            if self.credits <= 0:
                print("No more credits left! Game Over.")
                break

            self.print_cards(self.current_card)
            print(f"Your credits: {self.credits}")

            bet = self.get_bet()
            guess = input("Will the next card be higher, lower, or the same (h/l/s): ").strip().lower()

            if guess not in ['h', 'l', 's']:
                print("Invalid Input")
                continue

            next_card = self.deck.get_card()
            next_card.reveal()
            self.print_cards(self.current_card, next_card)

            if guess == 's' and next_card.value == self.current_card.value:
                winnings = int(bet * 5)
                self.credits += winnings
                print(f"Correct! Same card 5x bonus -> You won {winnings} credits. You now have {self.credits}.")
            elif ((guess == 'h' and next_card.value > self.current_card.value) or
                  (guess == 'l' and next_card.value < self.current_card.value)):
                final_mult = self.calculate_final_multiplier(self.current_card, guess, bet)
                winnings = int(bet * final_mult)
                self.credits += winnings
                print(f"Correct! x{final_mult} multiplier -> You won {winnings} credits. You now have {self.credits}.")
            else:
                self.credits -= bet
                print(f"Wrong guess. You lose {bet} credits. You now have {self.credits}.")

            self.current_card = next_card

        print("Thanks for playing!")



if __name__ == "__main__":
    game = Game() # Create a game object
    game.start_game() # Run the game