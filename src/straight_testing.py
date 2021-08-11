import poker_main
import itertools

card_rankings = {9: "Royal Flush",
                 8: "Straight Flush",
                 7: "Four of a Kind",
                 6: "Full House",
                 5: "Flush",
                 4: "Straight",
                 3: "Three of a Kind",
                 2: "Two Pair",
                 1: "Pair",
                 0: "High Card"}

dealer_cards = [(2, 'clubs'), (4, 'hearts'), (5, 'spades'), (3, 'hearts'), (14, 'diamonds'), (9, 'diamonds')]

player_cards = []

suits = ["clubs", "spades", "diamonds", "hearts"]
values = {"2": 2,
          "3": 3,
          "4": 4,
          "5": 5,
          "6": 6,
          "7": 7,
          "8": 8,
          "9": 9,
          "10": 10,
          "J": 11,
          "Q": 12,
          "K": 13,
          "A": 14}

cards = []
for suit in suits:
    for value in values:
        cards.append((values[value], suit))

frequency_table = {0: 0,
                   1: 0,
                   2: 0,
                   3: 0,
                   4: 0,
                   5: 0,
                   6: 0,
                   7: 0,
                   8: 0,
                   9: 0}

player = {"cards": [],
          "player_cards": [],
          "suits": {"hearts": 0,
                    "diamonds": 0,
                    "clubs": 0,
                    "spades": 0},
          "values": {i: 0 for i in range(2, 15)}}

player["cards"] += dealer_cards
player["card_values"] = [card[0] for card in player["cards"]]

new = poker_main.new_straight_check(player)
old = poker_main.straight_check(player)

print(f"new: {new}")
print(f"old: {old}")
