import random
import random as rand
import itertools
from collections import Counter


class Poker(object):
    """
    A class that plays a single game of poker
    """

    def __init__(self, players: list):
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

        self.pot = 0.0
        self.deck = [(value, suit) for suit in self.suits for value in self.values.values()]
        self.remaining_deck = self.deck.copy()

        self.players = players
        self.player_hands = {}
        self.number_of_players = len(self.players)
        self.seat_numbers = list(range(self.number_of_players))
        self.active_players = [player.active for player in self.players if player.active is True]
        self.betting_rounds = ["pre-flop", "post-flop", "turn", "river"]

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

        pre_flop_order = ["UTG", "UTG+1", "UTG+2", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
        post_flop_order = ["SB", "BB", "UTG", "UTG+1", "UTG+2", "LJ", "HJ", "CO", "BTN"]

        removal_order = [4, 3, 2, 5, 6, 7, 8]

        # rename positions based on the number of players
        if self.number_of_players < 9:

            # delete unnecessary players and get a playing order
            for j in range(0, 9 - self.number_of_players):
                del self.positions[removal_order[j]]

        self.pre_flop_order = [x for x in pre_flop_order if x in self.positions.values()]
        self.post_flop_order = [x for x in post_flop_order if x in self.positions.values()]

        self.player_positions = dict((player.current_position, player) for player in self.players)

    def deal(self):
        for player in self.players:
            self.player_hands[player] = random.sample(self.deck, 2)
            self.remaining_deck = [card for card in self.remaining_deck if card not in self.player_hands[player]]

    def post_blinds(self):
        for player in self.players:
            if player.current_position == "SB":
                player.chips -= 0.5
                self.pot += 0.5
                print(f"{player.name} posts small blind and now has {player.chips} BB")
            elif player.current_position == "BB":
                player.chips -= 1.0
                self.pot += 1.0
                print(f"{player.name} posts big blind and now has {player.chips} BB")
            else:
                continue

        print(f"Pot is currently: {self.pot} BB's big")

    def betting_action(self, betting_round="pre-flop"):
        # TODO: What happens when a player is all in?
        for player in self.player_positions.values():
            player.to_act = True

        i = 0
        current_bet_size = 0

        # while there is still a player to act
        while any([player.to_act for player in self.player_positions.values()]):

            # collect actions
            round_actions = []

            if betting_round == "pre-flop":
                order = self.pre_flop_order
                actions = {p: p.pre_flop_actions for p in self.player_positions.values()}
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

            for position in self.pre_flop_order:

                # check if position still active (this could be removed by changing the for loop iterator
                if position not in self.player_positions:
                    continue

                # check to see if any player is still active
                if not any([player.to_act for player in self.players]):
                    break

                player = self.player_positions[position]

                # get current action from player
                # should this come as just one list or interactively?
                if not actions[player]:
                    player.active = False
                    player.to_act = False
                    continue

                current_action = actions[player][i]
                print(f"{player}: {current_action}")

                # not sure if this is useful at all
                round_actions.append(current_action)

                # if player is not active for whatever reason remove them from active_players
                if not player.active:
                    del self.player_positions[position]
                    continue

                # if fold make the player is inactive
                if "fold" in current_action:
                    player.active = False
                    player.to_act = False
                    del self.player_positions[position]

                # if a player calls their balance loses a big blind and they remain active until all players are done
                if "call" in current_action:
                    player.chips -= current_bet_size
                    self.pot += current_bet_size
                    player.to_act = False

                # betting increase pot size
                if "bet" in current_action:
                    current_bet_size = float(current_action.split()[1])
                    player.chips -= current_bet_size
                    self.pot += current_bet_size

                    # once a bet is made all other players in the hand now have to act
                    for active_player in self.player_positions.values():
                        active_player.to_act = True
                    player.to_act = False

            i += 1


    def flop(self):
        pass

    def turn(self):
        pass

    def river(self):
        pass

    def showdown(self):
        pass

    def summary(self):
        pass

    def play_game(self):
        print("A poker game!")

        # deal cards
        self.deal()

        # post_blinds
        self.post_blinds()

        for betting_round in self.betting_rounds:
            self.active_players = [player for player in self.players if player.active is True]
            if len(self.active_players) == 1:
                winner = self.active_players[0]
                print(f"{self.active_players[0].name} wins {self.pot}")
                break
            print("-" * 80)
            print(str(betting_round).center(80))
            print("-" * 80)
            self.betting_action(betting_round=betting_round)

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

        self.chips = chips
        self.name = name
        self.deck = [(value, suit) for suit in self.suits for value in self.values.values()]
        self.cards = cards
        self.table_cards = table_cards
        self.in_play_cards = self.cards + self.table_cards
        self.remaining_deck = [card for card in self.deck if card not in self.in_play_cards]
        self.small_blind = False
        self.big_blind = False

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

        # self.card_values = [card[0] for card in self.in_play_cards]
        # self.card_values_counter = Counter(self.card_values)
        # self.card_suits = [card[1] for card in self.in_play_cards]

        # self.ranking = self.analyse_cards()

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

    def analyse_cards(self):

        player_card_rankings = []

        # check for straight
        straight_cards, hand_ranking, straight_ranking = self.straight_check()

        if straight_cards:
            player_card_rankings.append((hand_ranking, straight_ranking, straight_cards))

        # check for flush or straight flush
        flush_cards, flush, flush_ranking = self.flush_check(straight_cards)
        if flush:
            player_card_rankings.append((flush, flush_ranking, flush_cards))

        # check for all x-of-a-kind
        four_of_a_kind, three_of_a_kind, pairs = self.n_check()

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

    def __repr__(self):
        return repr(f'{self.name}, {self.chips} BB')
