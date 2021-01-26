import random as rand
import itertools
from collections import Counter

# rand.seed(43)  # two pair

rand.seed(83)

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

deck = set()
for suit in suits:
    for value in values:
        deck.add((values[value], suit))


def make_player(card_set):
    return {"cards": sorted(card_set)}


def new_straight_check(player):

    if not len(set(player["card_values"])) > 4:
        return None, None, None

    straight_values = [combo for combo in itertools.combinations(player["card_values"], 5)
                       if sorted(combo) == [2, 3, 4, 5, 14] or max(combo) - min(combo) == 4 and len(set(combo)) == 5]

    if straight_values:
        return list(max(straight_values))[::-1], 4, max(max(straight_values))
    return None, None, None


def straight_check(player):
    # adds A to start to check A-2-3-4-5 straight
    straight_test = [14 if 14 in player["card_values"] else 0] + [key if key in player["card_values"] else 0
                                                                  for key in values.values()]

    # group off cards that are present or not into lists in a list
    # this may seem a bit involved but should be useful
    # later for analysis of possible straights available after turn, river etc.
    list_of_groups = [list(group)[::-1] for k, group in itertools.groupby(straight_test, key=lambda x: x != 0)][::-1]

    # if any straight found
    for group in list_of_groups:

        # if a group of 5 that isn't full of zeros
        if len(group) >= 5 and not all(val == 0 for val in group):
            if len(group) > 5:
                group = group[0:-(len(group) - 5)]
            straight_ranking = max(group)

            return group, 4, straight_ranking

    # otherwise return None, None to show no straight was found
    return None, None, None


def flush_check(player, straight_cards=None):
    # Check if any flush is found

    card_counts = Counter(player["card_suits"])

    if any(val >= 5 for val in card_counts.values()):

        # flush suit
        flush_suit = max(card_counts, key=card_counts.get)

        # get flush cards
        flush_cards = [card for card in player["cards"] if card[1] == flush_suit]

        # check for any straight flush
        if straight_cards:

            if all(x in straight_cards for x in [card[0] for card in flush_cards]):
                # check for specific case of royal flush
                if all(x[0] in [10, 11, 12, 13, 14] for x in flush_cards):
                    # it is impossible for 2 players to have a royal flush so just return 9
                    return flush_cards, 9, None

                flush_ranking = max([card[0] for card in flush_cards if card[0] in straight_cards])
                return flush_cards, 8, flush_ranking

        flush_ranking = max([card[0] for card in flush_cards])
        return flush_cards, 5, flush_ranking
    else:
        return None, None, None


def n_check(player):
    pairs_of_cards = []
    three_of_a_kind_cards = []
    four_of_a_kind_cards = []

    for key, value in player["card_values_counter"].items():
        if value == 4:
            four_of_a_kind_cards += [key]
        elif value == 3:
            three_of_a_kind_cards += [key]
        elif value == 2:
            pairs_of_cards += [key]

    return four_of_a_kind_cards, three_of_a_kind_cards, pairs_of_cards


def analyse_init(player):
    player["card_values"] = [card[0] for card in player["cards"]]
    player["card_values_counter"] = Counter(player["card_values"])
    player["card_suits"] = [card[1] for card in player["cards"]]


def analyse_cards(player):
    analyse_init(player)

    player_card_rankings = []

    # check for straight
    straight_cards, hand_ranking, straight_ranking = new_straight_check(player)

    if straight_cards:
        player_card_rankings.append((hand_ranking, straight_ranking, straight_cards))

    # check for flush or straight flush
    flush_cards, flush, flush_ranking = flush_check(player, straight_cards)
    if flush:
        player_card_rankings.append((flush, flush_ranking, flush_cards))

    # NEW check for all kinds of cards
    four_of_a_kind, three_of_a_kind, pairs = n_check(player)

    # if four of a kind
    # four_of_a_kind = n_check(player, 4)
    if four_of_a_kind:
        player_card_rankings.append(
            (7, max(four_of_a_kind), [card for card in player["cards"] if card[0] == max(four_of_a_kind)]))
    elif pairs and three_of_a_kind:
        # full house
        player_card_rankings.append((6, max(three_of_a_kind), [card for card in player["cards"] if
                                                               card[0] == max(three_of_a_kind) or card[0] == max(
                                                                   pairs)]))
    elif three_of_a_kind:
        player_card_rankings.append(
            (3, max(three_of_a_kind), [card for card in player["cards"] if card[0] == max(three_of_a_kind)]))
    elif pairs:
        if len(pairs) > 1:
            # two pair
            highest_pairs = pairs[-2:]
            highest_pair_ranking = max(pairs)
            player_card_rankings.append(
                (2, highest_pair_ranking, [card for card in player["cards"] if card[0] in highest_pairs]))
        else:
            highest_pair = pairs[0]
            player_card_rankings.append(
                (1, highest_pair, [card for card in player["cards"] if card[0] == highest_pair]))
    else:
        player_card_rankings.append((0, max([card[0] for card in player["cards"]]), max(player["cards"])))

    highest_combination = max(player_card_rankings, key=lambda x: x[0])

    return highest_combination
