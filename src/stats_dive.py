import poker_main
from poker_main import deck, make_player, analyse_cards
import itertools
import random


def pre_flop_stats(players=None, n=100):
    # a function that runs a simulation for n games to see how likely a player is to win pre flop against other hands

    # set up
    winnners_dict = {k: 0 for k in players.keys()}

    # used cards are cards that can no longer come out of the deck
    used_cards = list(itertools.chain(*players.values()))

    # cards remaining in deck
    remaining_cards = [card for card in deck if card not in used_cards]

    for i in range(n):

        hand_ranks = []
        ranking_dict = {}
        # generate table cards from remaining deck
        table_cards = random.sample(remaining_cards, 5)

        for name, opponent_values in players.items():
            opponent = make_player(opponent_values + table_cards)
            opponent_ranking = analyse_cards(opponent)
            ranking_dict[name] = opponent_ranking

        winning_list = [k for k, v in ranking_dict.items() if v == max(ranking_dict.values())]
        # if len(winning_list) > 1:
        #'    continue

        for winner in winning_list:
            winnners_dict[winner] += 1

    for key, value in winnners_dict.items():
        winnners_dict[key] = 100 * value / n

    return winnners_dict


opponents = {"bobson-dugnutt": [(14, 'spades'), (14, 'diamonds')],
             "billy-bear": [(13, 'hearts'), (13, 'diamonds')],
             "johnny-mca": [(9, 'clubs'), (10, 'clubs')]}

for i in range(2, 14):
    opponents["johnny-mca"] = [(i, 'clubs'), (i + 1, 'clubs')]
    x = pre_flop_stats(players=opponents, n=100000)
    print(f"Percentage chance of suited {i}, {i + 1} winning is {x['johnny-mca']}")
