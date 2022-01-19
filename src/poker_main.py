import random
import itertools
from collections import Counter
from copy import deepcopy


class Card(object):
    def __init__(self, string):
        """

        Args:
            rank: str
                Card ranking. options are 'hearts', 'clubs', 'spades', 'diamonds'
            suit: str
                Suit options are 'A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'
        """

        self.ranks_to_values = {"2": 2,
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
                                "A": 14}
        self.values_to_ranks = {value: key for key, value in self.ranks_to_values.items()}

        self.rank = string[0]
        self.value = self.ranks_to_values[self.rank]
        self.suit = string[1]

        self.all_suits = {
            "s": "\u2660",
            "h": "\u2665",
            "c": "\u2663",
            "d": "\u2666",
        }

    def __repr__(self):
        return str(f"{self.rank}{self.all_suits[self.suit]}")

    def __str__(self):
        return str(f"{self.rank}{self.all_suits[self.suit]}")

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def __eq__(self, other):
        return (self.value == other.value) and (self.suit == other.suit)

    def __hash__(self):
        return hash(str(self))


class Poker(object):
    """
    A class that plays a single game of poker
    """

    def __init__(self, players: list, table_cards=None):

        self.suits = ["c", "s", "d", "h"]
        self.hand_values = {"2": 2,
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
                            "A": 14}
        self.hand_rankings = {value: key for key, value in self.hand_values.items()}

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

        self.pot = 0.0
        self.deck = [Card(value + suit) for suit in self.suits for value in self.hand_values]
        self.remaining_deck = deepcopy(self.deck)

        self.players = players
        self.player_hands = {}
        self.number_of_players = len(self.players)
        self.seat_numbers = list(range(self.number_of_players))
        self.active_players = [player.active for player in self.players if player.active is True]
        self.betting_rounds = ["pre-flop", "post-flop", "turn", "river"]

        if table_cards:
            # TODO: this is messy and needs tidied
            self.table_cards = table_cards
            if len(table_cards) < 3:
                self.flop_cards = table_cards
            if len(table_cards) >= 3:
                self.flop_cards = self.table_cards[0:3]
            if len(table_cards) >= 4:
                self.turn_card = table_cards[3]
            else:
                self.table_cards = []
            if len(table_cards) >= 5:
                self.river_card = table_cards[4]
            else:
                self.river_card = []
        else:
            self.table_cards = []
            self.flop_cards = []
            self.turn_card = []
            self.river_card = []

        self.actions = {"pre-flop": [],
                        "flop": [],
                        "turn": [],
                        "river": []}

        self.positions = {0: "SB",
                          1: "BB",
                          2: "UTG",
                          3: "UTG+1",
                          4: "UTG+2",
                          5: "LJ",
                          6: "HJ",
                          7: "CO",
                          8: "BTN"}

        self.positions_keys = dict((v, k) for k, v in self.positions.items())

        # pre- and post-flop betting orders are different due to big blinds
        pre_flop_order = ["UTG", "UTG+1", "UTG+2", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
        post_flop_order = ["SB", "BB", "UTG", "UTG+1", "UTG+2", "LJ", "HJ", "CO", "BTN"]

        # order removing players if there are less than 9
        removal_order = [4, 3, 2, 5, 6, 7, 8]

        # rename positions based on the number of players
        if self.number_of_players < 9:

            # delete unnecessary players and get a playing order
            for j in range(0, 9 - self.number_of_players):
                del self.positions[removal_order[j]]

        self.pre_flop_order = [x for x in pre_flop_order if x in self.positions.values()]
        self.post_flop_order = [x for x in post_flop_order if x in self.positions.values()]

        self.player_positions = dict((player.current_position, player) for player in self.players)
        self.showdown_card_analysis = None
        self.winners = None

        # a side pot = current pot + (1 + N(call/raise)) * all_in_raise_size
        self.number_of_pots = 1

    def deal(self):
        """
        Deals cards to each player than does not already have a set hand
        Returns:

        """
        print("=" * 40)

        if self.table_cards:
            self.remaining_deck = [card for card in self.remaining_deck if card not in self.table_cards]

        # players split into those already dealt and not dealt so cards are not dealt twice
        pre_dealt_players = [player for player in self.players if player.cards != []]
        other_players = [player for player in self.players if player.cards == []]

        for player in pre_dealt_players:

            # if player cards are already defined then remove from deck and don't deal them cards
            self.remaining_deck = [card for card in self.remaining_deck if card not in player.cards]
            self.player_hands[player] = player.cards
            print_cards = ""
            for card in self.player_hands[player]:
                print_cards += str(card)
            print(f"{player.name}: {print_cards}")

        for player in other_players:
            self.player_hands[player] = random.sample(self.remaining_deck, 2)
            self.remaining_deck = [card for card in self.remaining_deck if card not in self.player_hands[player]]
            player.cards = self.player_hands[player]
            print_cards = ""
            for card in self.player_hands[player]:
                print_cards += str(card)
            print(f"{player.name}: {print_cards}")
            self.remaining_deck = [card for card in self.remaining_deck if card not in self.player_hands[player]]

        print("=" * 40)

    def post_blinds(self):
        """
        Takes a small blind from player in the SB position and a big blind from a player in the BB position
        """
        for player in self.players:
            if player.current_position == "SB":
                player.chips -= 0.5
                self.pot += 0.5
                player.called_for = 0.5
                print(f"{player.name} posts small blind")
            elif player.current_position == "BB":
                player.chips -= 1.0
                self.pot += 1.0
                player.called_for = 1.0
                print(f"{player.name} posts big blind")
            else:
                continue

    def betting_action(self, betting_round="pre-flop"):
        """
        Args:
            betting_round: str
                Defines the current betting round. Options are 'pre-flop', 'post-flop', 'turn' and 'river'

        """

        # initialise all players as still to act
        for player in self.player_positions.values():
            player.to_act = True

        i = 0

        # collect actions
        round_actions = []
        current_raise_size = 0

        # players are no longer active after they fold
        while any([player.to_act for player in self.player_positions.values() if player.active]):
            if betting_round == "pre-flop":
                actions = {p: p.pre_flop_actions for p in self.player_positions.values()}
                order = self.pre_flop_order
            elif betting_round == "post-flop":
                order = self.post_flop_order
                actions = {p: p.post_flop_actions for p in self.player_positions.values()}
            elif betting_round == "turn":
                order = self.post_flop_order
                actions = {p: p.turn_actions for p in self.player_positions.values()}
            elif betting_round == "river":
                order = self.post_flop_order
                actions = {p: p.river_actions for p in self.player_positions.values()}
            else:
                raise ValueError("betting_round value not valid. only "
                                 "'pre_flop', 'post_flop', 'turn', 'river' are valid.")

            for position in order:

                # check if position still active (this could be removed by changing the for loop iterator
                if position not in self.player_positions:
                    continue

                # check to see if any player is still active
                if not any([player.to_act for player in self.players if player.to_act]):
                    break

                player = self.player_positions[position]

                # get current action from player
                # should this come as just one list or interactively?
                if not actions[player]:
                    player.active = False
                    player.to_act = False
                    continue

                current_action = actions[player][i]
                print(f"{player} {current_action}")

                round_actions.append(current_action)

                # if player is not active for whatever reason remove them from active_players
                if not player.active:
                    del self.player_positions[position]
                    continue

                # if action is fold make the player inactive
                if "fold" in current_action:
                    player.active = False
                    player.to_act = False
                    del self.player_positions[position]

                # if check, need to stay active but not to act
                if "check" in current_action:
                    player.to_act = False

                # if a player calls their balance loses the amount needed to call, and they remain active until all
                # players are done. The player.called_for handles if there is a call and reraise
                if "call" in current_action:
                    if current_raise_size >= player.chips + player.called_for:
                        print(f"{player.name} is all in")
                        player.all_in = True
                        player.active = False
                        self.number_of_pots += 1
                        player.side_pot_final_raise_size = player.chips + player.called_for

                    if player.called_for:
                        player.chips -= (current_raise_size - player.called_for)
                        self.pot += (current_raise_size - player.called_for)
                    else:
                        player.chips -= current_raise_size
                        self.pot += current_raise_size

                    player.called_for = current_raise_size
                    player.to_act = False

                # betting increases pot size and decreases players chip pile
                if "raise to" in current_action:
                    raise_size = float(current_action.split()[2])
                    if raise_size > player.chips + player.called_for:
                        raise ValueError("Raise size is larger than number of chips player has.")
                    elif raise_size == player.chips + player.called_for:
                        player.all_in = True
                        print(f"{player.name} is all in!")
                        player.active = False

                    if player.called_for:
                        player.chips -= (raise_size - player.called_for)
                        self.pot += (raise_size - player.called_for)
                    else:
                        player.chips -= raise_size
                        self.pot += raise_size

                    current_raise_size = raise_size
                    player.called_for = current_raise_size

                    # once a bet is made all other active players in the hand now have to act
                    if not player.all_in:
                        for active_player in self.player_positions.values():
                            active_player.to_act = True

                    player.to_act = False

            i += 1

        print("-" * 40)
        for player in self.players:
            player.called_for = 0
        print(f"Pot size is {self.pot} BB")
        print("=" * 40)

    def call_bet(self):


        pass
    def flop(self):
        """
        flop deals 3 table cards if not already defined
        Returns:

        """
        if not self.flop_cards:
            self.flop_cards = random.sample(self.remaining_deck, 3)
            self.table_cards += self.flop_cards
            for card in self.flop_cards:
                self.remaining_deck.remove(card)

        print_flop_cards = ""
        for card in self.flop_cards:
            print_flop_cards += str(card)
        print(f"Flop cards: {print_flop_cards}")

    def turn(self):
        """
        deals turn card if not already defined
        Returns:

        """
        if not self.turn_card:
            self.turn_card = random.sample(self.remaining_deck, 1)[0]
            self.table_cards.append(self.turn_card)
            self.remaining_deck.remove(self.turn_card)

        print(f"Turn card: {self.turn_card}")
        print_table_cards = ""
        for card in self.table_cards:
            print_table_cards += str(card)
        print(f"Table Cards: {print_table_cards}")

    def river(self):
        """
        deals river card if not already defined
        Returns:

        """
        if not self.river_card:
            self.river_card = random.sample(self.remaining_deck, 1)[0]
            self.table_cards.append(self.river_card)
            self.remaining_deck.remove(self.river_card)

        print(f"River card: {self.river_card}")
        print_table_cards = ""
        for card in self.table_cards:
            print_table_cards += str(card)
        print(f"Table Cards: {print_table_cards}")

    def showdown(self):
        """
        If game gets to showdown, this function determines the winner and how the pot is chopped up

        TODO: multiway all in pots

        Returns:

        """
        self.showdown_card_analysis = BoardAnalysis(self.players, self.table_cards)
        self.winners = self.showdown_card_analysis.winners

    def summary(self):
        print("-" * 40)
        for player in self.players:
            string_cards = "".join([str(x) for x in player.cards])
            print(f"{player.name}({string_cards}): {player.print_ranking}")
            print("-"*40)

        for player in self.winners:
            player.chips += self.pot / len(self.showdown_card_analysis.winners)
        if len(self.winners) == 1:
            print(
                f"Winner is {self.winners[0].name} with {self.showdown_card_analysis.print_analysis[self.winners[0].name]} "
                f"and collects {self.pot}")
        else:
            winners_str = " ".join(x.name for x in self.winners[:-1]) + " and " + self.winners[-1].name

            print(f"Winners are {winners_str} and win {self.pot / len(self.winners)} BB each with {self.showdown_card_analysis.print_winning_combination}")

    def play_game(self):

        # deal cards
        if not all([player.cards for player in self.players]):
            self.deal()

        # post_blinds
        self.post_blinds()

        all_in = False  # bool determines if betting rounds should be skipped due to players all in
        for betting_round in self.betting_rounds:

            self.active_players = [player for player in self.players if player.active]
            if betting_round == "post-flop":
                self.flop()
            elif betting_round == "turn":
                self.turn()
            elif betting_round == "river":
                self.river()
            print("=" * 40)
            print(str(betting_round).center(40))
            print("=" * 40)
            if not all_in:
                self.betting_action(betting_round=betting_round)

            self.active_players = [player for player in self.players if player.active]

            if len(self.active_players) - len([player.all_in for player in self.active_players if player.all_in]) == 1 \
                    and not all_in:
                print("No more betting as a player(s) are all in")
                print("=" * 40)
                all_in = True
                continue

            if len(self.active_players) == 1 and not all_in:
                winner = self.active_players[0]
                winner.chips += self.pot
                print(f"{winner.name} wins {self.pot} BB and has {winner.chips} BB")
                self.pot = 0
                break

        self.showdown()
        self.summary()

    def __repr__(self):
        return repr(f'Poker Game {self.players}')


class Player(object):
    """
    A class for a poker player.
    """

    def __init__(self, name: str, chips: float, cards=None, table_cards=None, current_position=None,
                 pre_flop=None, post_flop=None, turn=None, river=None):

        if pre_flop is None:
            pre_flop = []
        if post_flop is None:
            post_flop = []
        if turn is None:
            turn = []
        if river is None:
            river = []
        if table_cards is None:
            table_cards = []
        if cards is None:
            cards = []

        self.suits = ["c", "s", "d", "h"]
        self.values = {"2": 2,
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
                       "A": 14}
        self.hand_ranking = []
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

        self.chips = chips
        self.name = name
        self.deck = [Card(value + suit) for suit in self.suits for value in self.values]
        self.cards = cards
        self.table_cards = table_cards
        self.known_cards = self.table_cards + self.cards
        self.in_play_cards = self.cards + self.table_cards
        self.remaining_deck = [card for card in self.deck if card not in self.in_play_cards]
        self.small_blind = False
        self.big_blind = False
        self.all_in = False
        if not current_position:
            self.current_position = None
        else:
            self.current_position = current_position
        self.active = True
        self.to_act = False

        self.pre_flop_actions = pre_flop
        self.post_flop_actions = post_flop
        self.turn_actions = turn
        self.river_actions = river
        self.called_for = 0
        self.print_ranking = None

        # self.card_values = [card[0] for card in self.in_play_cards]
        # self.card_values_counter = Counter(self.card_values)
        # self.card_suits = [card[1] for card in self.in_play_cards]

        # self.ranking = self.analyse_cards()

    def __repr__(self):
        return str(f'{self.name}')


class BoardAnalysis(object):
    def __init__(self, players=None, table_cards=None):

        if table_cards is None:
            table_cards = []
        if players is None:
            players = []
        self.players = players
        self.table_cards = table_cards
        self.suits = ["c", "s", "d", "h"]
        self.values = {"2": 2,
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
                       "A": 14}

        self.values_to_ranks = {value: key for key, value in self.values.items()}

        self.rankings = {9: "a royal flush",
                         8: "a straight flush",
                         7: "four of a kind",
                         6: "a full house",
                         5: "a flush",
                         4: "a straight",
                         3: "three of a kind",
                         2: "two Pair",
                         1: "a pair",
                         0: "high card"}

        self.deck = [Card(value + suit) for suit in self.suits for value in self.values]
        self.all_player_cards = [player.cards for player in self.players]

        # this should be tidied up to have the in_play_cards as a list rather than list of lists
        self.in_play_cards = self.all_player_cards + [self.table_cards]
        self.in_play_cards = set([item for sublist in self.in_play_cards for item in sublist])
        self.remaining_deck = [card for card in self.deck if card not in self.in_play_cards]
        self.test_rankings = {}
        self.data_analysis, self.print_analysis = self.analyse_cards()
        self.winners = self.data_analysis["winners"]
        self.print_winning_combination = self.winners[0].print_ranking
        self.ranked_players = {}

    @staticmethod
    def straight_check(cards):
        """
        Checks for a straight in a set of cards

        Args:
            cards: list
                cards to check for a straight combination in

        Returns:

        """
        if not len(set(cards)) > 4:
            return None, None, None, None
        card_values = [x.value for x in cards]
        straight_values = [combo for combo in itertools.combinations(card_values, 5)
                           if sorted(combo) == [2, 3, 4, 5, 14] or
                           max(combo) - min(combo) == 4 and len(set(combo)) == 5]

        if straight_values:
            straight_cards = sorted([x for x in cards if x.value in straight_values[0]],
                                    key=lambda x: x.value,
                                    reverse=False)
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
            flush_cards = sorted([card for card in cards if card.suit == flush_suit],
                                 key=lambda x: x.value,
                                 reverse=True)[0:5]
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
                        flush_ranking = max([card.value for card in flush_cards if card in straight_cards])

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
        rankings = {}
        print_rankings = {}
        data_rankings = {}

        for player in self.players:

            # combine players cards and table cards to give rankable list
            player_card_rankings = player.hand_ranking
            all_cards = self.table_cards + player.cards

            # check for straight
            straight_values, straight_cards, hand_ranking, straight_ranking = self.straight_check(all_cards)
            if straight_cards:
                final_straight_cards = []
                for card in straight_cards:
                    if card.value in straight_values:
                        final_straight_cards.append(card)
                        straight_values.remove(card.value)

                # for A-low straight
                if all([x.value in [14, 2, 3, 4, 5] for x in straight_cards]):
                    final_straight_cards.insert(0, final_straight_cards.pop())
                final_straight_cards.reverse()
                player_card_rankings.append((4, final_straight_cards, straight_ranking, []))

            # check for flush or straight flush
            flush_cards, flush, flush_ranking = self.flush_check(all_cards, straight_cards)
            if flush:
                player_card_rankings.append((flush, flush_cards, flush_ranking, sorted([x.value for x in flush_cards],
                                                                                       reverse=True)))

            # check for all x-of-a-kind
            four_of_a_kind, three_of_a_kind, pairs = self.n_check(all_cards)

            # check for of a kind
            if four_of_a_kind:
                four_of_a_kind_cards = [card for card in all_cards if card.value == max(four_of_a_kind)]
                if len(four_of_a_kind_cards) > 4:
                    raise ValueError("Cannot be more than four-of-a-kind")
                kickers = max([card for card in all_cards if card.value != max(four_of_a_kind)], key=lambda x: x.value)
                four_of_a_kind_cards.append(kickers)
                player_card_rankings.append(
                    (7, four_of_a_kind_cards, max(four_of_a_kind), [kickers.value]))

            # full house
            elif pairs and three_of_a_kind:
                full_house_cards = [card for card in all_cards if
                                    card.value == max(three_of_a_kind) or card.value == max(pairs)]
                ranking = dict(Counter([x.value for x in full_house_cards]))
                ranking = {v: k for k, v in ranking.items()}
                ranking = [ranking[3], ranking[2]]
                player_card_rankings.append((6, full_house_cards, max(three_of_a_kind), ranking))

            elif three_of_a_kind:
                three_of_a_kind_cards = [card for card in all_cards if card.value == max(three_of_a_kind)]
                kickers = sorted(self.maxN([x for x in all_cards if x not in three_of_a_kind_cards], n=2),
                                 key=lambda x: x.value, reverse=True)
                kicker_values = [kicker.value for kicker in kickers]
                player_card_rankings.append((3, three_of_a_kind_cards + kickers, max(three_of_a_kind), kicker_values))

            elif pairs:
                if len(pairs) > 1:
                    # two pair
                    highest_pairs = sorted(pairs, reverse=True)[:2]
                    highest_pair_ranking = max(pairs)
                    kickers = sorted(self.maxN([x for x in all_cards if x.value not in highest_pairs], n=1),
                                     key=lambda x: x.value, reverse=True)
                    kicker_values = [x.value for x in kickers]
                    player_card_rankings.append(
                        (2, sorted([card for card in all_cards if card.value in highest_pairs], reverse=True) + kickers, highest_pair_ranking,
                         kicker_values))
                else:
                    highest_pair = pairs[0]
                    kickers = sorted(self.maxN([x for x in all_cards if x.value != highest_pair], n=3),
                                     key=lambda x: x.value, reverse=True)
                    kicker_values = [x.value for x in kickers]
                    player_card_rankings.append(
                        (1, [card for card in all_cards if card.value == highest_pair] + kickers, highest_pair,
                         kicker_values))
            else:
                kickers = sorted(self.maxN(all_cards, n=5), key=lambda x: x.value, reverse=True)
                kicker_values = [x.value for x in kickers]
                player_card_rankings.append(
                    (0, self.maxN(all_cards, n=5), max([card.value for card in all_cards]), kicker_values))

            highest_combination = max(player_card_rankings, key=lambda x: x[0])
            rankings[player.name] = highest_combination
            data_rankings[player.name] = (
                highest_combination[0], highest_combination[1], highest_combination[2], highest_combination[3])
            self.test_rankings[player.name] = HandRanking(highest_combination)
            hand_ranking_string = self.ranking_string(highest_combination[0], highest_combination[1])
            player.print_ranking = hand_ranking_string
            print_rankings[player.name] = hand_ranking_string

        # defines the maximum combination
        self.test_rankings = sorted(self.test_rankings.values(), reverse=True)
        max_combination = max(data_rankings.values())
        max_combination_players = {k: v for k, v in data_rankings.items() if v == max_combination}

        # defines the maximum ranking of the combination
        max_ranking = max([x[1] for x in max_combination_players.values()])
        max_ranking_players = {k: v for k, v in max_combination_players.items() if v[1] == max_ranking}

        # defines the maximum kickers
        max_kicker = max([x[2] for x in max_ranking_players.values()])
        max_ranking_players_with_kickers = {k: v for k, v in max_ranking_players.items() if v[2] == max_kicker}

        winners = max_ranking_players_with_kickers.keys()
        data_rankings["winners"] = list([x for x in self.players if x.name in winners])
        print_rankings["winners"] = list([x for x in self.players if x.name in winners])

        return data_rankings, print_rankings

    @staticmethod
    def ranking_string(rank, cards):
        """
        A function that parses the raw ranking data


        Returns:

        """
        string_cards = "".join([str(x) for x in cards])
        ranking_strings = {
            0: f"high card: {string_cards[:2]} with kickers {string_cards[2:]}",
            1: f"a pair: {string_cards[0:4]} with kickers {string_cards[4:]}",
            2: f"two pair: {string_cards[0:8]} with {string_cards[8:]} kicker",
            3: f"three of a kind: {string_cards[0:6]} with {string_cards[6:]} kickers",
            4: f"a straight: {string_cards}",
            5: f"a flush: {string_cards}",
            6: f"a full house: {string_cards}",
            7: f"four of a kind: {string_cards[0:8]}",
            8: f"a straight flush: {string_cards}",
            9: f"a royal flush: {string_cards}"
        }

        return ranking_strings[rank]

    def __str__(self):
        return str(f"{self.print_analysis}")


class InteractivePoker(Poker):
    """
    An extension to the Poker class that allows for interactive play;
    """

    def __init__(self, num_players, num_bots, players: list):
        super().__init__(players)
        self.num_players = num_players
        self.num_bots = num_bots

    pass


class HandRanking(object):
    """
    A class for a players hand ranking
    """
    def __init__(self, hand_data):
        self.hand_class = hand_data[0]
        self.cards = hand_data[1]
        self.hand_ranking = hand_data[2]
        self.kickers = hand_data[3]

        self.single_parameter = [self.hand_class] + self.cards
        print(self.single_parameter)

    def __str__(self):
        return "".join([str(x) for x in self.cards])

    def __repr__(self):
        return "".join([str(x) for x in self.cards])

    def __lt__(self, other):
        return self.single_parameter < other.single_parameter

    def __gt__(self, other):
        return self.single_parameter > other.single_parameter

    def __eq__(self, other):
        return self.single_parameter == other.single_parameter

    def __hash__(self):
        return hash(str(self))
