import poker_main
from poker_main import make_player, deck
import itertools
import random

random.seed(1690)


# dealer_cards = [(9, 'clubs'), (9, 'clubs'), (9, 'clubs'), (9, 'clubs'), (10, 'clubs')]
# dealer_cards = [(2, 'clubs'), (3, 'hearts'), (5, 'spades'), (7, 'hearts'), (14, 'diamonds')]
# dealer_cards = [(3, 'clubs'), (3, 'hearts'), (5, 'spades'), (7, 'hearts'), (14, 'diamonds')]
# dealer_cards = [(3, 'clubs'), (3, 'hearts'), (5, 'spades'), (5, 'hearts'), (14, 'diamonds')]
# dealer_cards = [(3, 'clubs'), (3, 'hearts'), (3, 'spades'), (5, 'hearts'), (14, 'diamonds')]
# dealer_cards = [(3, 'clubs'), (4, 'hearts'), (5, 'spades'), (6, 'hearts'), (7, 'diamonds')]
# dealer_cards = [(2, 'clubs'), (4, 'clubs'), (5, 'clubs'), (6, 'clubs'), (7, 'clubs')]
# dealer_cards = [(2, 'clubs'), (2, 'hearts'), (3, 'hearts'), (3, 'clubs'), (3, 'diamonds')]
# dealer_cards = [(4, 'clubs'), (4, 'hearts'), (4, 'spades'), (4, 'diamonds'), (3, 'diamonds')]
# dealer_cards = [(9, 'clubs'), (10, 'clubs'), (11, 'clubs'), (12, 'clubs'), (13, 'clubs')]


def heads_up_poker(self_cards: list, table_cards=None, opponents_cards=None):
    records = {}

    # sort own cards
    self_cards = sorted(self_cards)

    # cards minus the players pair
    cards_minus_player_cards = [card for card in deck if card not in self_cards]

    # list of wins for each pair of pocket cards
    win_list = []

    # for 1000 sets of dealer cards
    if not table_cards:
        table_cards = random.sample(cards_minus_player_cards, 5)

    # cards available after pair and dealer cards taken out
    cards_minus_dealer_and_player_cards = [card for card in cards_minus_player_cards if card not in table_cards]

    # make player
    self_player = make_player(self_cards + table_cards)

    # analyse player cards and return stats
    my_stats = poker_main.analyse_cards(self_player)

    if not opponents_cards:
        opponents_cards = random.sample(cards_minus_dealer_and_player_cards, 2)

    opponent = make_player(opponents_cards + table_cards)
    opponent_stats = poker_main.analyse_cards(opponent)

    records["opponent"] = opponent_stats

    # if player wins
    if my_stats == max([my_stats, opponent_stats]):
        return 1, my_stats, opponent_stats, table_cards
    else:
        return 0, my_stats, opponent_stats, table_cards


test = [(10, 'spades'), (14, 'clubs')]
other = [(14, 'hearts'), (9, 'diamonds')]
table = [(7, 'clubs'), (6, 'diamonds'), (7, 'hearts'), (5, 'hearts'), (12, 'spades')]

x, player, oppo, table_cards = heads_up_poker(self_cards=test, table_cards=table, opponents_cards=other)


"""wins = 0
num_of_trials = 100000
for i in range(num_of_trials):
    x, player, oppo, table = heads_up_poker(self_cards=test, opponents_cards=other)
    wins += x

win_percentage = 100 * wins / num_of_trials"""
"""
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
for i, combination in enumerate(itertools.combinations(cards, 5)):
    player = {"cards": [],
              "player_cards": [],
              "suits": {"hearts": 0,
                        "diamonds": 0,
                        "clubs": 0,
                        "spades": 0},
              "values": {i: 0 for i in range(2, 15)}}

    player["cards"] += combination

    hand = poker_main.analyse_cards(player)
    frequency_table[hand[0]] += 1

for key, val in frequency_table.items():
    freq = 100 * val / 2598960
    print(f"A {card_rankings[key]} occurs roughly {freq} % of the time")
# pairs = poker_main.n_check(player, 2)"""
