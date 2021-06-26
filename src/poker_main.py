import random as rand
import itertools
from collections import Counter


class Player(object):
    """
    The
    """

    def __init__(self, cards, table_cards):
        self.suits = ["clubs", "spades", "diamonds", "hearts"]
        self.values = {"2": 2,
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

        self.rankings = {9: "royal_flush",
                         8: "straight_flush",
                         7: "four_of_a_kind",
                         6: "full_house",
                         5: "flush",
                         4: "straight",
                         3: "three_of_a_kind",
                         2: "two_pair",
                         1: "pair",
                         0: "high_card"}

        self.deck = set((value, suit) for suit in self.suits for value in self.values.values())
        self.cards = cards
        self.ranking = None  # yet
        self.table_cards = table_cards

    def straight_check(self):
        """
        Checks for a straight in a set of cards

        Args:
            self:

        Returns:

        """
        if not len(set(self.card_values)) > 4:
            return None, None, None

        straight_values = [combo for combo in itertools.combinations(self.card_values, 5)
                           if sorted(combo) == [2, 3, 4, 5, 14] or
                           max(combo) - min(combo) == 4 and len(set(combo)) == 5]

        if straight_values:
            return list(max(straight_values))[::-1], 4, max(max(straight_values))
        return None, None, None

    def flush_check(self, straight_cards=None):
        """
        Checks for a flush in a given set of cards
        Args:
            player:
            straight_cards:

        Returns:

        """

        card_counts = Counter(self.card_suits)

        if any(val >= 5 for val in card_counts.values()):

            # flush suit
            flush_suit = max(card_counts, key=card_counts.get)

            # get flush cards
            flush_cards = [card for card in self.cards if card[1] == flush_suit]

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

    def n_check(self):
        """
        Checks for n number of cards with the same numerical value

        Args:
            player:

        Returns:

        """
        pairs_of_cards = []
        three_of_a_kind_cards = []
        four_of_a_kind_cards = []

        for key, value in self.card_values_counter.items():
            if value == 4:
                four_of_a_kind_cards += [key]
            elif value == 3:
                three_of_a_kind_cards += [key]
            elif value == 2:
                pairs_of_cards += [key]

        return four_of_a_kind_cards, three_of_a_kind_cards, pairs_of_cards

    def initialise_player_cards(self):
        """
        Initialises a players cards for analysis
        Args:
            player:

        Returns:

        """
        self.card_values = [card[0] for card in self.cards]
        self.card_values_counter = Counter(self.card_values)
        self.card_suits = [card[1] for card in self.cards]

    def analyse_cards(self):
        self.initialise_player_cards()

        player_card_rankings = []

        # check for straight
        straight_cards, hand_ranking, straight_ranking = self.straight_check()

        if straight_cards:
            player_card_rankings.append((hand_ranking, straight_ranking, straight_cards))

        # check for flush or straight flush
        flush_cards, flush, flush_ranking = self.flush_check(straight_cards)
        if flush:
            player_card_rankings.append((flush, flush_ranking, flush_cards))

        # NEW check for all kinds of cards
        four_of_a_kind, three_of_a_kind, pairs = self.n_check()

        # if four of a kind
        # four_of_a_kind = n_check(player, 4)
        if four_of_a_kind:
            player_card_rankings.append(
                (7, max(four_of_a_kind), [card for card in self.cards if card[0] == max(four_of_a_kind)]))
        elif pairs and three_of_a_kind:
            # full house
            player_card_rankings.append((6, max(three_of_a_kind), [card for card in self.cards if
                                                                   card[0] == max(three_of_a_kind) or card[0] == max(
                                                                       pairs)]))
        elif three_of_a_kind:
            player_card_rankings.append(
                (3, max(three_of_a_kind), [card for card in self.cards if card[0] == max(three_of_a_kind)]))
        elif pairs:
            if len(pairs) > 1:
                # two pair
                highest_pairs = pairs[-2:]
                highest_pair_ranking = max(pairs)
                player_card_rankings.append(
                    (2, highest_pair_ranking, [card for card in self.cards if card[0] in highest_pairs]))
            else:
                highest_pair = pairs[0]
                player_card_rankings.append(
                    (1, highest_pair, [card for card in self.cards if card[0] == highest_pair]))
        else:
            player_card_rankings.append((0, max([card[0] for card in self.cards]), max(self.cards)))

        highest_combination = max(player_card_rankings, key=lambda x: x[0])

        return highest_combination
