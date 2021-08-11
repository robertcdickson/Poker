import itertools
import random
import re
import pandas as pd
from collections import Counter

from src.poker_main import Player


class PokerGame(object):
    # TODO: Implement a situation loader which can load a state of play and simulate the rest of the game n times
    # TODO: dict object for where all players are positioned

    def __init__(self, game_text, data, table_cards, winners, winning_hands, hero="Bobson_Dugnutt", game_index=0):
        """

        Args:
            game_text (str):
                The whole text read out from the pokerstars output file
            data (Dataframe):
                A dataframe with different attributes of the game
            table_cards (str):
                String of cards on table
            winners (list):
                List of the winners of the game
            winning_hands (list):
                List of hands that won the game
            game_index (int):
                An index used to track PokerStarsCollection games
        """
        self.suits = {"c": "clubs",
                      "s": "spades",
                      "d": "diamonds",
                      "h": "hearts"}

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

        self.deck = set((value, suit) for suit in self.suits for value in self.values.values())
        self.data = data
        self.game_index = game_index
        self.game_text = game_text
        self.winners = winners
        self.winning_hands = winning_hands

        if table_cards:
            self.table_cards = table_cards
        else:
            self.table_cards = None

        self.big_blind = self.get_blind("Big")
        self.small_blind = self.get_blind("Small")
        self.chip_leader = self.data.index[self.data["Chips"] == self.data["Chips"].max()].to_list()
        self.hero = hero

        self.player_cards_text = self.get_player_cards()
        if self.player_cards_text is not None:
            self.player_cards = self.translate_hand(self.player_cards_text.split())

        self.player_names = None
        self.player_final_action = None

        self.final_pot = self.get_final_pot()

    def get_blind(self, size: str):
        return self.data.index[self.data[f"{size.capitalize()} Blind"] == True].to_list()

    def translate_hand(self, hand):
        # translates hands from pokerstars output format to list of tuples
        return [(int(self.values[card[0]]), self.suits[card[1]]) for card in hand]

    def get_player_cards(self):
        for line in self.game_text:
            if "Dealt" in line and self.hero in line:
                return line.split("[")[-1].rstrip("]\n")

    def get_final_pot(self):
        for line in self.game_text:
            if "collected" in line:
                return float(line.split("$")[1].split()[0].strip("()"))

    def simulate_game(self, players=None, n=100, use_table_cards=True, table_card_length=None):
        """
        A function that runs a simulation for n poker_session to see how likely a hero is to win pre flop against
        other hands
        Args:
            players:
            n_table_cards:
            specified_table_cards:
            n:

        Returns:

        """

        # set up
        winners_dict = {k: 0 for k in players.keys()}
        ties_dict = {k: 0 for k in players.keys()}
        table_cards_dict = {}

        # used cards are cards that can no longer come out of the deck
        used_cards = list(itertools.chain(*players.values()))

        # simulates the game n times
        for i in range(n):

            ranking_dict = {}

            # get ranking of each hand with the set of table cards
            for name, player_cards in players.items():
                opponent_ranking = Player(player_cards, self.table_cards).analyse_cards()
                ranking_dict[name] = (opponent_ranking[0], opponent_ranking[1])

            # get a list of winners in hand
            winning_list = [k for k, v in ranking_dict.items() if v == max(ranking_dict.values())]
            table_cards_dict[i] = self.table_cards

            # determine if single winner of if there was a draw
            for winner in winning_list:
                if len(winning_list) > 1:
                    ties_dict[winner] += 1
                else:
                    winners_dict[winner] += 1

        for key, value in winners_dict.items():
            winners_dict[key] = 100 * value / n
        for key, value in ties_dict.items():
            ties_dict[key] = 100 * value / n

        return winners_dict, ties_dict, table_cards_dict

    def __str__(self):

        print_winners = ""
        for winner in self.winners:
            print_winners += f"{winner} "
        print_winners.lstrip(" ")

        print_winning_hands = ""
        for winning_hand in self.winning_hands:
            print_winning_hands += winning_hand
        print_winning_hands.lstrip(" ")

        if print_winning_hands == "":
            print_winning_hands = "Not Shown"

        if self.table_cards is None:
            print_table_cards = "Not dealt"
        else:
            print_table_cards = self.table_cards

        line = "-" * max([len(y) for y in ["Winners: " + print_winners,
                                           "Winning Cards: " + print_table_cards,
                                           "Table Cards: " + print_winning_hands]])
        return f'Poker Game #{self.game_index}\n' + \
               line + "\n" + \
               f'Winners: {print_winners}\n' \
               f'Winning Cards: {print_winning_hands}\n' \
               f'Table Cards: {print_table_cards}\n' + \
               line + "\n"


class PokerStarsCollection(object):
    def __init__(self, file, working_dir, hero="Bobson_Dugnutt", write_files=False):

        self.suits = {"c": "clubs",
                      "s": "spades",
                      "d": "diamonds",
                      "h": "hearts"}

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

        self.file = file
        self.working_dir = working_dir
        self.hero = hero

        self.games_text = self.process_file(split_files=write_files)
        self.games_data = {}
        i = 0
        for key, game in self.games_text.items():
            self.games_data[key] = self.read_pokerstars_file(lines=game, game_index=i)
            i += 1

        self.winners = [game.winners[0] for game in self.games_data.values()]
        self.winner_count = Counter(self.winners)

    def process_file(self, split_files=False):

        # a function that chunks a file of poker stars hands into individual poker_session
        files_dict = {}
        file_number = 0

        with open(self.file, "r") as rf:

            line_marker = 0

            # start and write markers need for starting/stopping of file chunk
            start = False
            write = False

            for line in rf.readlines():
                if "PokerStarsCollection Hand" in line:
                    start = True
                    write = True
                    files_dict[file_number] = []
                    if split_files:
                        wf = open(f"{self.working_dir}/hand_{file_number}.txt", "w")

                if start:
                    if write:
                        files_dict[file_number].append(line)
                        if split_files:
                            wf.write(line)

                    if line == "\n":
                        line_marker += 1

                    # if 2 \n tokens found then the poker game is finished and the writing of the file ends
                    if line_marker == 2:
                        line_marker = 0
                        write = False
                        if split_files:
                            wf.close()
                        file_number += 1

        return files_dict

    @staticmethod
    def read_hand(hand, hand_regex):
        # reads in a hand given a hand regex
        return hand_regex.findall(hand)[0].strip("[]").split()

    def translate_hand(self, hand):
        # translates hands from pokerstars output format to list of tuples
        return [(self.values[card[0]], self.suits[card[1]]) for card in hand]

    def read_hand_file(self, file):
        # define regex for later reading
        hand_regex = re.compile("\[.*\]")

        # Dealt and Board are the only two parts of pokerstars file that include cards (besides shown which isn't
        # implemented yet
        with open(file, "r") as rf:
            for line in rf.readlines():
                if "Dealt" in line:
                    hand = self.read_hand(line, hand_regex)
                    translated_hand = self.translate_hand(hand)
                if "Board" in line:
                    board = self.read_hand(line, hand_regex)
                    translated_board = self.translate_hand(board)

        return translated_hand, translated_board

    def get_button_seat(self, file):
        # returns the index of the seat currently on the button
        with open(file, "r") as rf:
            return int(re.search("#\d", rf.readlines()[1]).group().strip("#"))

    def split_game_to_events(self, file, lines):
        # takes in a pokerstars game and returns a dictionary with different pieces of data
        data_dicts = {}
        if file:
            with open(file, "r") as rf:
                key = "HEADER"
                data_dicts[key] = []
                for line in rf.readlines():
                    if "***" in line:
                        if any(x in line for x in ["RIVER"]):
                            table_cards = re.search(r'\[.*\]', line).group().replace("[", "").replace("]", "")
                            data_dicts["TABLE_CARDS"] = table_cards
                        key = re.search(r'\*\*\*.*\*\*\*', line).group().strip("* ")
                        data_dicts[key] = []
                    else:
                        data_dicts[key].append(line)
                return data_dicts
        if lines:
            key = "HEADER"
            data_dicts[key] = []
            for line in lines:
                if "***" in line:
                    if any(x in line for x in ["RIVER"]):
                        table_cards = re.search(r'\[.*\]', line).group().replace("[", "").replace("]", "")
                        data_dicts["TABLE_CARDS"] = table_cards
                    key = re.search(r'\*\*\*.*\*\*\*', line).group().strip("* ")
                    data_dicts[key] = []
                else:
                    data_dicts[key].append(line)
            return data_dicts

    def read_pre_deal_lines(self, player_list):

        data_dict = {"Player Name": [],
                     "Seat Number": [],
                     "Chips": []}

        button_seat = int(re.search("#\d", player_list[1]).group().strip("#"))

        for line in player_list:
            player = re.findall(":.*\(", line)
            if player and "chips" in line:
                # get hero name and number of chips
                line_list = line.split(" ")

                # get different pieces of data pre dealing
                seat_number = int(line_list[1].strip(":"))
                player_name = re.sub('[:\( ]', '', player[0])
                chips = float(line_list[-4].strip("($"))  # THIS MAY BE A PROBLEM TEST

                data_dict["Player Name"].append(player_name)
                data_dict["Seat Number"].append(seat_number)
                data_dict["Chips"].append(chips)

        # renumber seat numbers for ordering of play
        new_seat_order = [i for i in range(1, len(data_dict["Seat Number"]) + 1)]
        data_dict["Play Order"] = []
        new_button = new_seat_order[data_dict["Seat Number"].index(button_seat)]

        for seat in new_seat_order:
            if int(seat) - new_button < 0:
                data_dict["Play Order"].append(seat - new_button + len(data_dict["Seat Number"]))
            elif int(seat) - new_button > 0:
                data_dict["Play Order"].append(seat - new_button)
            else:
                data_dict["Play Order"].append(len(data_dict["Seat Number"]))

        data_dict["Betting Order"] = [i - 2 if i - 2 > 0 else i - 2 + len(data_dict["Play Order"]) for i in
                                      data_dict["Play Order"]]
        data_dict["Big Blind"] = [True if j == 2 else False for j in data_dict["Play Order"]]
        data_dict["Small Blind"] = [True if j == 1 else False for j in data_dict["Play Order"]]

        data_df = pd.DataFrame(data_dict).set_index(["Player Name"])
        conditions = [

            (data_df["Seat Number"] - new_button < 0),
            (data_df["Seat Number"] - new_button > 0),
            (data_df["Seat Number"] - new_button == 0),

        ]
        choices = [
            seat - new_button + len(data_dict["Seat Number"]),
            seat - new_button,
            len(data_dict["Seat Number"])
        ]
        return data_df

    def read_betting_action(self, lines_list, play_phase=None):
        data = {}
        for line in lines_list:

            if "Dealt" in line:
                player_name = line.split()[2]
                # data["Player Name"].append(player_name)
                cards = [line.split()[3].lstrip("["), line.split()[4].rstrip("]")]

            elif ":" in line:
                player_name = line.split(":")[0]
                action = line.split(":")[1].rstrip()
                if player_name not in data.keys():
                    data[player_name] = [action]
                else:
                    data[player_name].append(action)

        normalised_dict = dict([(k, pd.Series(v)) for k, v in data.items()])
        df = pd.DataFrame(normalised_dict).transpose()
        df.columns = [f"{play_phase.capitalize()} Action {i}" for i in range(1, len(df.columns) + 1)]
        return df

    def operations(self, operator, line):
        return {
            "showed": re.findall("\[.*\]", line)[0],
        }.get(operator, None)

    def read_summary(self, lines_list):
        data = {}
        winners = []
        winning_hands = []
        for line in lines_list:
            if "showed" in line:
                a = re.sub("\(.*\)", "", line.split("showed")[0])
                b = re.sub("Seat [0-9]: ", "", a).strip()
                data[b] = re.findall("\[.+]", line)[0].strip("[]")
                if "won" in line:
                    if "showed" in line:
                        winning_hands.append(data[b])
                    winners.append(b)
            elif "mucked" in line:
                a = re.sub("\(.*\)", "", line.split("mucked")[0])
                b = re.sub("Seat [0-9]: ", "", a).strip()
                data[b] = re.findall("\[.+]", line)[0].strip("[]")
            elif "collected" in line:
                a = re.sub("\(.*\)", "", line.split("collected")[0])
                b = re.sub("Seat [0-9]: ", "", a).strip()
                winners.append(b)

        return pd.DataFrame(data.values(), index=data.keys(), columns=["Player Cards"]), winners, winning_hands

    def get_final_table_cards(self, lines):
        for line in reversed(lines):
            if "Board" in line:
                return re.findall("\[.+]", line)[0].strip("[]")
        return None

    def read_pokerstars_file(self, lines, game_index=0):
        """
        A function that processes a pokerstars game and returns a dataframe with a summary of all events in game

        Args:
            lines:
            file (str): file to read

        Returns:
            events df (pandas df)
        """

        data_dict = {}

        # process file
        game_text = self.split_game_to_events(file=None, lines=lines)

        # get table cards
        table_cards = self.get_final_table_cards(game_text["SUMMARY"])

        # pre-deal data
        data_dict["pre_action"] = self.read_pre_deal_lines(game_text["HEADER"])

        search_dict = {"deal": "HOLE CARDS",
                       "flop": "FLOP",
                       "turn": "TURN",
                       "river": "RIVER",
                       "showdown": "SHOW DOWN"}

        for key, value in search_dict.items():
            try:
                data_dict[key] = self.read_betting_action(game_text[value], play_phase=key)
            except KeyError:
                break

        data_dict["summary"], winners, winning_hands = self.read_summary(game_text["SUMMARY"])
        events_df = pd.concat([val for val in data_dict.values()], axis=1)
        game = PokerGame([item for sublist in game_text.values() for item in sublist], events_df, table_cards,
                         winners=winners, winning_hands=winning_hands, game_index=game_index)
        return game

    def winning_games(self, winner=None):
        """

        Args:
            player: str
                Name of winning player
        Returns:
            winner_dict

        """
        if not winner:
            winner = self.player
        return {game.game_index: game for game in self.games_data.values() if winner in game.winners}
