import random as rand
import itertools
import operator

# rand.seed(1690)
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

# generate cards
cards = {}

# makes dictionary with all cards
for suit in suits:
    for value in values:
        cards[f"{value}-{suit}"] = (values[value], suit)

# number of players and number of dealer cards
num_of_players = 3
dealer = 5

# get a random sample of cards that are to be in play
play_cards = rand.sample(list(cards.values()), dealer + 2 * num_of_players)

# distribute cards
dealer_cards = play_cards[0:5]
# player_1_cards = [(10, 'clubs'), (11, 'clubs')]
# player_1_cards = [(10, 'clubs'), (10, 'spades')]
player_1_cards = play_cards[5:7]
player_2_cards = play_cards[7:9]
player_3_cards = play_cards[9:11]

# dictionary of rankings
ranking = {9: "royal_flush",
           8: "straight_flush",
           7: "four_of_a_kind",
           6: "full_house",
           5: "flush",
           4: "straight",
           3: "three_of_a_kind",
           2: "two_pair",
           1: "pair",
           0: "high_card"}

# initialise a players cards with different connections

player_card_combinations = {"cards": [],
                            "player_cards": [],
                            "pairs": [],
                            "highest_card": None,
                            "highest_pair": (None, None),
                            "suits": {"hearts": 0,
                                      "diamonds": 0,
                                      "clubs": 0,
                                      "spades": 0},
                            "values": {i: 0 for i in range(2, 15)}}

dealer_card_combinations = {"cards": [],
                            "pairs": [],
                            "highest_card": [],
                            "highest_pair": (None, None),
                            "suits": {"hearts": 0,
                                      "diamonds": 0,
                                      "clubs": 0,
                                      "spades": 0},
                            "values": {i: 0 for i in range(2, 15)}
                            }
suit_matching = 0
number_matching = 0
number_in_a_row = 0

player_card_combinations["cards"] += player_1_cards
player_card_combinations["player_cards"] = player_1_cards

high_card_check = [a for a in player_1_cards if a[0] == max([x[0] for x in player_1_cards])]
player_card_combinations["highest_card"] = high_card_check

player_card_combinations["suits"][player_1_cards[0][1]] += 1
player_card_combinations["suits"][player_1_cards[1][1]] += 1

player_card_combinations["values"][player_1_cards[0][0]] += 1
player_card_combinations["values"][player_1_cards[1][0]] += 1

# pre-flop analysis
for a, b in itertools.combinations(player_1_cards, 2):

    # if pocket pairs found
    if a[0] == b[0]:
        print(f"Player has pocket {a[0]}\'s")
        player_card_combinations["pairs"] += [(a, b)]
        player_card_combinations["highest_pair"] = (a, b)

    # if same suit found
    if a[1] == b[1]:
        print(f"Player has two {a[1]}")

# flop
visible_dealer_cards = dealer_cards[0:3]

for a in visible_dealer_cards:
    player_card_combinations["cards"] += [a]
    player_card_combinations["values"][a[0]] += 1
    player_card_combinations["suits"][a[1]] += 1
    # for b in player_1_cards:

# turn
turn = dealer_cards[3]
player_card_combinations["cards"] += [turn]
player_card_combinations["values"][turn[0]] += 1
player_card_combinations["suits"][turn[1]] += 1

# river
river = dealer_cards[4]
player_card_combinations["cards"] += [river]
player_card_combinations["values"][river[0]] += 1
player_card_combinations["suits"][river[1]] += 1


def analyse_cards(player):
    ranking = 0

    # if True, player has a straight THIS IS NOT TRUE!!!
    if any(val >= 5 for val in player['values']):
        ranking = 4

    # if True, player has a flush
    if any(val >= 5 for val in player['suit']):
        ranking = 5
        flush_suit = max(cards.items(), key=(lambda key: cards[key]))
        flush_cards = sorted([card for card in cards if card[1] == flush_suit])

        # check royal flush
        royal_flush_values = [10, 11, 12, 13, 14]
        if all((value, flush_suit) in player['cards'] for value in royal_flush_values):
            ranking = 9
            return ranking

        # check straight flush
        flush_values = [flush_card[0] for flush_card in flush_cards]
        flush_value_differences = [flush_value - min(list(flush_values)) - int(flush_cards.index(flush_value)) for
                                   flush_value in flush_values]
        if all(diff == 0 for diff in flush_value_differences):
            ranking = 8
            return ranking

        # if four of a kind
        if any(val == 4 for val in player['values'].values()):
            ranking = 7

        # if three of a kind
        if any(val == 3 for val in player['values'].values()):
            ranking = 3

        # if single pair
        if any(val == 2 for val in player['values'].values()):

            # check number of pair
            number_of_pairs = 0
            for val in player['values']:
                if player['values'][val] == 2:
                    number_of_pairs += 1

            # if more than one pair set to two pairs ranking
            if number_of_pairs > 1:
                ranking = 2
            ranking = 1

        # check full house
        if any(val == 3 for val in player['values'].values()) and any(val == 2 for val in player['values'].values()):
            ranking = 6
            
"""# check combinations in flop
for a, b in itertools.combinations(visible_dealer_cards, 2):

    # if suit and value don't match for pair of cards then continue
    if a[0] != b[0] and a[1] != b[1]:
        continue

    print(a, b)
    # if a pair in flop
    if a[0] == b[0]:
        print(f"Pair of {a[0]}\'s on flop")
        player_card_combinations["pairs"] = (a, b)
        if a[0] > player_card_combinations["highest_pair"][0]:
            player_card_combinations["highest_pair"] = (a, b)

    # if same suit found
    if a[1] == b[1]:
        print(f"Flop has two {a[1]}")"""

"""for pair in list(itertools.product(player_1_cards, visible_dealer_cards)):
    print(pair)"""

"""player_suits = []
dealer_suits = []
player_numbers = []
dealer_numbers = []

# for each size of possible pool
for i in range(2, len(dealer_cards) + 1):
    # for each card in a players hand
    for card in player_1_cards:

        # get all possible combinations of hand card and length i of dealer cards
        check = list(itertools.combinations(sorted([card] + dealer_cards), i))

        # split check into cards with and without the hand card
        for combo in check:

            len_set = set(x[1] for x in combo)
            len_list = list(combo)
            test = len(len_set) < len(len_list)
            if test:
                if card in len_list:
                    player_suits.append(len_list)
                else:
                    dealer_suits.append(len(len_list) - len(len_set))
            suits.append(len_list)
        # itertools.groupby()"""

"""sui((6, 'clubs'), (8, 'diamonds'), (4, 'diamonds'), (14, 'diamonds'), (12, 'diamonds')), ((7, 'diamonds'), (6, 'clubs'), (4, 'diamonds'), (14, 'diamonds'), (12, 'diamonds')), ((7, 'diamonds'), (6, 'clubs'), (8, 'diamonds'), (4, 'diamonds'), (12, 'diamonds')), ((7, 'diamonds'), (6, 'clubs'), (8, 'diamonds'), (4, 'diamonds'), (14, 'diamonds')), ((7, 'diamonds'), (6, 'clubs'), (8, 'diamonds'), (14, 'diamonds'), (12, 'diamonds')), ((7, 'diamonds'), (8, 'diamonds'), (4, 'diamonds'), (14, 'diamonds'), (12, 'diamonds'))ts
if pair in hand instantly put ranking to 8
if same suit in hand makes it easier to get flush, but doesn't give a ranking change
if numbers in range of each other then makes it easier for straight, but doesn't give a ranking change.


card1, card2
card1, card2, card3, 

"""
