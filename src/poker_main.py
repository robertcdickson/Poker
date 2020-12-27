import random as rand
import itertools

rand.seed(1690)
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

cards = {}

for suit in suits:
    for value in values:
        cards[f"{value}-{suit}"] = (values[value], suit)

num_of_players = 3
dealer = 5

play_cards = rand.sample(list(cards.values()), dealer + 2 * num_of_players)

dealer_cards = play_cards[0:5]
player_1_cards = play_cards[5:7]
player_2_cards = play_cards[7:9]
player_3_cards = play_cards[9:11]

ranking = {"royal_flush": 0,
           "straight_flush": 1,
           "four_of_a_kind": 2,
           "full_house": 3,
           "flush": 4,
           "straight": 5,
           "three_of_a_kind": 6,
           "two_pair": 7,
           "pair": 8,
           "high_card": 9}

suit_matching = 0
number_matching = 0
number_in_a_row = 0

for a, b in itertools.combinations(player_1_cards, 2):
    if a[0] == b[0]:
        print(f"Player has pocket {a[0]}\'s")
        number_matching += 1

card_combinations = []
player_suits = []
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
        # itertools.groupby()

"""sui((6, 'clubs'), (8, 'diamonds'), (4, 'diamonds'), (14, 'diamonds'), (12, 'diamonds')), ((7, 'diamonds'), (6, 'clubs'), (4, 'diamonds'), (14, 'diamonds'), (12, 'diamonds')), ((7, 'diamonds'), (6, 'clubs'), (8, 'diamonds'), (4, 'diamonds'), (12, 'diamonds')), ((7, 'diamonds'), (6, 'clubs'), (8, 'diamonds'), (4, 'diamonds'), (14, 'diamonds')), ((7, 'diamonds'), (6, 'clubs'), (8, 'diamonds'), (14, 'diamonds'), (12, 'diamonds')), ((7, 'diamonds'), (8, 'diamonds'), (4, 'diamonds'), (14, 'diamonds'), (12, 'diamonds'))ts
if pair in hand instantly put ranking to 8
if same suit in hand makes it easier to get flush, but doesn't give a ranking change
if numbers in range of each other then makes it easier for straight, but doesn't give a ranking change.


card1, card2
card1, card2, card3, 

"""
