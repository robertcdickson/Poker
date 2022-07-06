import itertools
from src.poker_main import *


class SingleBoardAnalysis(object):
    def __init__(self, player_cards=None, table_cards=None, street=None):
        """

        Args:
            player_cards (list):

            table_cards (list):
        """

        if player_cards is None:
            player_cards = []

        if table_cards is None:
            table_cards = []
        if street is None:
            street = ""

        self.player_cards = player_cards
        self.table_cards = table_cards
        self.street = street

        self.suits = ["c", "s", "d", "h"]
        self.values = {
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "T": 10,
            "J": 11,
            "Q": 12,
            "K": 13,
            "A": 14,
        }

        self.values_to_ranks = {value: key for key, value in self.values.items()}

        self.rankings = {
            9: "a royal flush",
            8: "a straight flush",
            7: "four of a kind",
            6: "a full house",
            5: "a flush",
            4: "a straight",
            3: "three of a kind",
            2: "two Pair",
            1: "a pair",
            0: "high card",
        }

        self.deck = [Card(value + suit) for suit in self.suits for value in self.values]

        # this should be tidied up to have the in_play_cards as a list rather than list of lists
        self.in_play_cards = self.player_cards + self.table_cards

        self.remaining_deck = [
            card for card in self.deck if card not in self.in_play_cards
        ]

        self.test_rankings = {}
        self.data_analysis = self.analyse_cards()

        self.counter = {}

    @staticmethod
    def straight_check(cards):
        """
        Checks for a straight in a set of cards

        Args:
            cards: list
                cards to check for a straight combination in

        Returns:

        """
        # Need 5 cards for straight
        if not len(set(cards)) > 4:
            return None, None, None, None

        card_values = [x.value for x in cards]
        straight_values = [
            combo
            for combo in itertools.combinations(card_values, 5)
            if sorted(combo) == [2, 3, 4, 5, 14]
            or max(combo) - min(combo) == 4
            and len(set(combo)) == 5
        ]

        if straight_values:
            straight_cards = sorted(
                [x for x in cards if x.value in max(straight_values)],
                key=lambda x: x.value,
                reverse=False,
            )
            if all([x in straight_values[0] for x in [14, 2, 3, 4, 5]]):
                straight_ranking = 5
            else:
                straight_ranking = max(max(straight_values))
            return list(max(straight_values))[::-1], straight_cards, 4, straight_ranking

        return None, None, None, None

    @staticmethod
    def flush_check(cards, straight_cards=None):
        """
        Checks for a flush in a given set of cards
        Args:
            cards: list
                Cards for flush check
            straight_cards: list
                Cards determined to form a straight used to check for straight flushes

        Returns:

        """
        card_suits = [card.suit for card in cards]
        card_counts = Counter(card_suits)

        if any(val >= 5 for val in card_counts.values()):

            # flush suit
            flush_suit = max(card_counts, key=card_counts.get)

            # get flush cards
            # the reverse sorted and indexing is needed to remove clubs that are outside the top 5 highest value
            flush_cards = sorted(
                [card for card in cards if card.suit == flush_suit],
                key=lambda x: x.value,
                reverse=True,
            )[0:5]

            # check for any straight flush
            if straight_cards:

                if all(x in straight_cards for x in flush_cards):
                    # check for specific case of royal flush
                    if all(x.value in [10, 11, 12, 13, 14] for x in flush_cards):

                        # it is impossible for 2 players to have a royal flush so just return 9
                        return flush_cards, 9, 14

                    elif all(x.value in [14, 2, 3, 4, 5] for x in flush_cards):
                        flush_ranking = 5
                    else:
                        flush_ranking = max(
                            [
                                card.value
                                for card in flush_cards
                                if card in straight_cards
                            ]
                        )

                    return flush_cards, 8, flush_ranking

            flush_ranking = max([card.value for card in flush_cards])
            return flush_cards, 5, flush_ranking
        else:
            return None, None, None

    @staticmethod
    def maxN(elements, n):
        """

        Args:
            elements:  iterable
                list of elements from which the max n are to be found
            n:  int
                Number of maximum elements to choose

        Returns:

        """
        return sorted(elements, reverse=True, key=lambda x: x.value)[:n]

    @staticmethod
    def n_check(cards):
        """
        Checks for n number of cards with the same numerical value

        Args:
            cards: list
                Cards for checking pairs, three/four of a kind

        Returns:

        """
        pairs_of_cards = []
        three_of_a_kind_cards = []
        four_of_a_kind_cards = []

        for key, value in Counter([x.value for x in cards]).items():

            # There should never be a five-of-a-kind in most games but if there is it is limited to four-of-a-kind
            if value > 4:
                raise ValueError("Cannot be more than four-of-a-kind")
            if value == 4:
                four_of_a_kind_cards += [key]
            elif value == 3:
                three_of_a_kind_cards += [key]
            elif value == 2:
                pairs_of_cards += [key]

        return four_of_a_kind_cards, three_of_a_kind_cards, pairs_of_cards

    def analyse_cards(self):

        data_dict = {
            "Has Straight": False,
            "Straight Ranking": None,
            "Straight Cards": None,
            "Straight Street": None,

            "Has Flush": False,
            "Flush Ranking": None,
            "Flush Cards": None,
            "Flush Street": None,

            "Has Royal Flush": False,
            "Has Straight Flush": False,
            "Has Full House": False,
            "Has Four-Of-A-Kind": False,
            "Has Three-Of-A-Kind": False,
            "Has Two Pair": False,
            "Has One Pair": False,
            "Has High Card": False,
        }

        # combine players cards and table cards to give rankable list
        all_cards = self.in_play_cards

        # check for straight
        (
            straight_values,
            straight_cards,
            hand_ranking,
            straight_ranking,
        ) = self.straight_check(all_cards)

        if straight_cards:

            final_straight_cards = []

            for card in straight_cards:
                if card.value in straight_values:
                    final_straight_cards.append(card)
                    straight_values.remove(card.value)

            # for wheel
            if all([x.value in [14, 2, 3, 4, 5] for x in straight_cards]):
                final_straight_cards.insert(0, final_straight_cards.pop())

            final_straight_cards.reverse()

            data_dict["Has Straight"] = True
            data_dict["Straight Ranking"] = straight_ranking
            data_dict["Straight Cards"] = straight_cards

            if all([x in all_cards[:-2] for x in straight_cards]):
                data_dict["Straight Street"] = "Flop"
            elif all([x in all_cards[:-1] for x in straight_cards]):
                data_dict["Straight Street"] = "Turn"
            else:
                data_dict["Straight Street"] = "River"

        # check for flush or straight flush
        flush_cards, flush, flush_ranking = self.flush_check(all_cards, straight_cards)

        if flush:

            data_dict["Has Flush"] = True
            data_dict["Flush Ranking"] = flush_ranking
            data_dict["Flush Cards"] = flush_cards

            if all([x in all_cards[:-2] for x in flush_cards]):
                data_dict["Flush Street"] = "Flop"
            elif all([x in all_cards[:-2] for x in flush_cards]):
                data_dict["Flush Street"] = "Turn"
            else:
                data_dict["Flush Street"] = "River"

            # This is going to have a weird edge case when a flopped flush turns in to a straight flush need to add the
            # if all bit above here for that
            if flush == 9:
                data_dict["Has Royal Flush"] = True
            elif flush == 8:
                data_dict["Has Straight Flush"] = True

        # check for all x-of-a-kind
        four_of_a_kind, three_of_a_kind, pairs = self.n_check(all_cards)

        # check for 4-of-a-kind
        if four_of_a_kind:

            data_dict["Has Four-Of-A-Kind"] = True

            four_of_a_kind_cards = [
                card for card in all_cards if card.value == max(four_of_a_kind)
            ]

            kickers = max(
                [card for card in all_cards if card.value != max(four_of_a_kind)],
                key=lambda x: x.value,
            )

            four_of_a_kind_cards.append(kickers)
            data_dict["Four-Of-A-Kind Cards"] = four_of_a_kind_cards
            if not data_dict["Has Royal Flush"] or data_dict["Has Straight Flush"]:
                data_dict["Best Hand"] = four_of_a_kind_cards

        # full house
        elif pairs and three_of_a_kind:
            data_dict["Has Full House"] = True
            full_house_cards = [
                card
                for card in all_cards
                if card.value == max(three_of_a_kind) or card.value == max(pairs)
            ]

            # sorts by count 3 then by count 2
            full_house_cards = sorted(
                full_house_cards,
                key=lambda x: [a.value for a in full_house_cards].count(x.value),
                reverse=True,
            )
            data_dict["Full House Cards"] = full_house_cards

        elif three_of_a_kind:
            data_dict["Has Three-Of-A-Kind"] = True
            three_of_a_kind_cards = [
                card for card in all_cards if card.value == max(three_of_a_kind)
            ]
            kickers = sorted(
                self.maxN(
                    [x for x in all_cards if x not in three_of_a_kind_cards], n=2
                ),
                key=lambda x: x.value,
                reverse=True,
            )
            data_dict["Three-Of-A-Kind Cards"] = three_of_a_kind + kickers

        elif pairs:
            if len(pairs) > 1:
                data_dict["Has Two Pair"] = True

                # two pair
                highest_pairs = sorted(pairs, reverse=True)[:2]
                kickers = sorted(
                    self.maxN(
                        [x for x in all_cards if x.value not in highest_pairs], n=1
                    ),
                    key=lambda x: x.value,
                    reverse=True,
                )
                kicker_values = [x.value for x in kickers]
                data_dict["Two Pair Cards"] = highest_pairs + kickers

            else:
                data_dict["Has One Pair"] = True
                highest_pair = pairs[0]
                kickers = sorted(
                    self.maxN([x for x in all_cards if x.value != highest_pair], n=3),
                    key=lambda x: x.value,
                    reverse=True,
                )
                data_dict["One Pair Cards"] = [
                    card for card in all_cards if card.value == highest_pair
                ] + kickers
        else:
            data_dict["Has High Card"] = True
            kickers = sorted(
                self.maxN(all_cards, n=5), key=lambda x: x.value, reverse=True
            )
            data_dict["High Card Cards"] = kickers
            kicker_values = [x.value for x in kickers]

        return data_dict
