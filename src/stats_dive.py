import poker_main
from poker_main import deck, make_player, analyse_cards
import itertools
import random


def pre_flop_stats(players=None, n_table_cards=5, specified_table_cards=None, n=100):
    # a function that runs a simulation for n games to see how likely a player is to win pre flop against other hands

    # set up
    winners_dict = {k: 0 for k in players.keys()}
    draws_dict = {k: 0 for k in players.keys()}
    table_cards_dict = {}
    # used cards are cards that can no longer come out of the deck
    used_cards = list(itertools.chain(*players.values()))

    # cards remaining in deck
    remaining_cards = [card for card in deck if card not in used_cards]

    for i in range(n):

        hand_ranks = []
        ranking_dict = {}

        if not specified_table_cards:
            # generate table cards from remaining deck
            table_cards = random.sample(remaining_cards, n_table_cards)
        else:
            table_cards = specified_table_cards

        for name, opponent_values in players.items():
            opponent = make_player(opponent_values + table_cards)
            opponent_ranking = analyse_cards(opponent)
            print(f"Player {name} with ranking: {opponent_ranking}")
            ranking_dict[name] = (opponent_ranking[0], opponent_ranking[1])

        winning_list = [k for k, v in ranking_dict.items() if v == max(ranking_dict.values())]
        table_cards_dict[i] = table_cards
        for winner in winning_list:
            if len(winning_list) > 1:
                draws_dict[winner] += 1
            else:
                winners_dict[winner] += 1

    for key, value in winners_dict.items():
        winners_dict[key] = 100 * value / n
    for key, value in draws_dict.items():
        draws_dict[key] = 100 * value / n

    return winners_dict, draws_dict, table_cards_dict


opponents = {"bobson-dugnutt": [(2, 'diamonds'), (2, 'spades')],
             "johnny-three-socks": [(3, 'clubs'), (3, 'diamonds')]}
table_cards = [(5, 'spades'), (5, 'clubs'), (9, 'spades'), (9, 'clubs'), (14, 'hearts')]

wins, draws, tables = pre_flop_stats(players=opponents, n=1000, n_table_cards=5)
analysis = {}
"""for i in range(6, 14):

    against = {
        "suited_connectors": [(i, 'clubs'), (i + 1, 'clubs')],
        "unsuited_connectors": [(i, 'spades'), (i + 1, 'clubs')],
        "pairs": [(i, 'spades'), (i, 'clubs')]
    }

    opponents.update(against)
    x = pre_flop_stats(players=opponents, n=10000)
    analysis[i] = x
    print(f"Percentage chance of {opponents['bobson-dugnutt']} beating suited {i}, {i + 1}  is {x['bobson-dugnutt']}")"""
