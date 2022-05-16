import random
import os

ZERO = """
┌───────────┐
│    ___    │
│   / _ \   │
│  | | | |  │
│  | | | |  │
│  | |_| |  │
│   \___/   │
│           │
└───────────┘
""".strip()

ONE = """
┌───────────┐
│    __     │
│   /_ |    │
│    | |    │
│    | |    │
│    | |    │
│    |_|    │
│           │
└───────────┘
""".strip()

# TODO: I feel like the ASCII art in here can be improved.
TWO = """
┌───────────┐
│   ___     │
│  |__ \    │
│     ) |   │
│    / /    │
│   / /_    │
│  |____|   │
│           │
└───────────┘
""".strip()

THREE = """
┌───────────┐
│   ____    │
│  |___ \   │
│    __) |  │
│   |__ <   │
│   ___) |  │
│  |____/   │
│           │
└───────────┘
""".strip()

def add(*cards):
    "Adds multiple cards in one string, side by side."
    split = [card.split("\n") for card in cards]
    out = []

    for i in range(9):
        row = ""
        for card in split:
            row += card[i] + " "

        out.append(row.strip())

    return "\n".join(out)

# https://en.m.wikipedia.org/wiki/Fisher–Yates_shuffle
def shuffle(arr):
    """Shuffles a list using the Fisher-Yates algorithm."""
    n = len(arr)
    for i in range(n-1, 1, -1):
        j = random.randint(0, i)

        # Swap
        ti = arr[i]
        tj = arr[j]
        arr[i] = tj
        arr[j] = ti

    return arr


class Card:
    """Represents a card."""
    def __init__(self, number):
        self.number = number

    def get_suit(self):
        suits = ["♣", "♦", "♥", "♠"]
        return suits[self.number]

    def get_ascii(self):
        cards = [ZERO, ONE, TWO, THREE]
        return cards[self.number]

    def __str__(self):
        return "[{}{}]".format(self.number, self.get_suit())

def create_many(number, n=10):
    """Creates many cards of the same number."""
    cards = []
    for i in range(n):
        cards.append(Card(number))

    return cards

def flatten(t):
    """Flattens a list of lists."""
    return [item for sublist in t for item in sublist]

def create_deck():
    """Creates a deck of 40 cards and shuffles it."""
    return shuffle([
        *create_many(0),
        *create_many(1),
        *create_many(2),
        *create_many(3)
    ])

class Game:
    """Represents a round of the game Nim Type Zero."""
    def __init__(self):
        self.cards = create_deck()
        self.players = []
        self._cur_player = 0
        self.total = 0

    def current_player(self):
        return self.players[self._cur_player]

    def next_player(self):
        self._cur_player += 1

        if self._cur_player > len(self.players)-1:
            self._cur_player = 0

    def first_player(self):
        self._cur_player = 0
        return self.current_player()

    def add_player(self, name):
        player = Player(self, name)
        self.players.append(player)
        return player
    
    def draw(self):
        return self.cards.pop()

    def reset(self):
        # Create a new shuffled deck.
        self.cards = create_deck()

        # Reset players' hands
        for player in self.players:
            player.cards = []

        game.total = 0
        self._cur_player = 0

    def deal(self, n=4):
        """Deals n amount of cards to each player."""
        for i in range(n):
            for player in self.players:
                player.draw()

    def settle_bets(self, loser):
        loser.chips -= loser.bet
        amount = int(loser.bet / (len(self.players)-1))

        for player in self.players:
            # Reset bet
            player.bet = 0
            player.all_in = False

            if player.name == loser.name:
                continue

            player.chips += amount

    def bets_settled(self, highest_bet):
        # First bet is not even set yet.
        if highest_bet is None:
            return False

        # Check everyone called the highest bet or went all in
        for player in self.players:
            if player.bet < highest_bet and not player.all_in:
                return False

        return True

class Player:
    def __init__(self, game, name):
        self.game = game
        self.name = name
        self.cards = []
        self.chips = 100
        self.bet = 0
        self.all_in = False
        self.folded = False

    def draw(self):
        """Draws a card from the main deck."""
        card = self.game.draw()
        self.cards.append(card)
        return card

    def show_hand(self):
        """Shows the player's hand in a simple list format."""
        return add(*map(lambda card: card.get_ascii(), self.cards))
    
    def play(self, number):
        for i in range(len(self.cards)):
            card = self.cards[i]

            if card.number == number:
                self.cards.pop(i)
                self.game.total += card.number
                return True

        return False

def enter_bet(player, highest_bet=None):
    while True:
        try:
            bet = int(input("Enter bet: "))

            if bet > player.chips:
                print("Too high! Not enough chips.")
            else:
                if highest_bet is not None:
                    if bet < highest_bet:
                        print("That's not a raise, go higher.")
                        continue

                return bet
        except:
            print("Invalid Input. Try Again.")

def clear():
    os.system("cls" if os.name == "nt" else "clear")

game = Game()

players = int(input("How many players?: "))

print("Starting game with {} players.".format(players))

for i in range(players):
    game.add_player("Player {}".format(i+1))

rounds = 0
while True:
    rounds += 1

    if rounds > 3:
        print("Game Over. Final Results:")

        for p in game.players:
            print("{}'s chips: {}".format(p.name, p.chips))

        exit()

    game.reset()
    game.deal()

    first_bet = True
    highest_bet = None

    print("Betting for round {} started.".format(rounds))

    while not game.bets_settled(highest_bet):
        player = game.current_player()

        print("Highest Bet: {}".format(highest_bet))
        input("{}'s turn to bet. Press Enter.".format(player.name))
        print("{}'s hand:\n{}".format(player.name, player.show_hand()))
        print("You have {} chips.".format(player.chips))

        if first_bet:
            player.bet = enter_bet(player)
            highest_bet = player.bet
            first_bet = False
            clear()
            print("{} bets {} chips".format(player.name, player.bet))
        else:
            while True:
                cmd = input("call, fold or raise?: ").lower()

                if cmd not in ("call", "fold", "raise"):
                    print("Invalid input. Try again.")
                    continue
                
                if cmd == "call":
                    if player.chips > highest_bet:
                        player.bet = highest_bet
                    else:
                        player.bet = player.chips
                        player.all_in = True

                    clear()
                    print("{} Calls!".format(player.name))
                    break
                elif cmd == "raise":
                    player.bet = enter_bet(player, highest_bet)
                    highest_bet = player.bet

                    clear()
                    print("{} Raises!".format(player.name))
                    # print("Highest Bet: {}".format(highest_bet))
                    break
                elif cmd == "fold":
                    print("Fold not implemented.")

        game.next_player()

    print("Game Starting")
    game.first_player()
    while True:
        player = game.current_player()
        lose = False

        input("It's {}'s turn! Press Enter.".format(player.name))
        print("{}'s hand:\n{}".format(player.name, player.show_hand()))

        while True:
            try:
                number = int(input("Which number to play?: "))

                if not player.play(number):
                    print("You don't have that number.")
                else:
                    clear()
                    print("{} played {}".format(player.name, number))
                    print("Game Total: {}".format(game.total))

                    if game.total > 9:
                        print("{} loses.".format(player.name))
                        lose = True
                        game.settle_bets(player)

                        for player in game.players:
                            print("{}'s chips: {}".format(player.name,
                                player.chips))

                        if player.chips <= 0:
                            print("Game Over")
                            exit()
                    else:
                        game.next_player()
                    break
            except:
                print("Invalid Input. Try Again.")

        if lose:
            break
