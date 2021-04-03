import re
import pandas as pd


class PokerStars(object):
    def __init__(self, file, working_dir, player="Bobsondugnutt11", split_files=False):
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
        self.player = player

        self.games_text = self.process_file(split_files=split_files)
        self.games_data = {}
        for key, game in self.games_text.items():
            self.games_data[key] = self.read_pokerstars_file(lines=game)

    def process_file(self, split_files=False):

        # a function that chunks a file of poker stars hands into individual games
        files_dict = {}
        file_number = 0

        with open(self.file, "r") as rf:

            line_marker = 0

            # start and write markers need for starting/stopping of file chunk
            start = False
            write = False

            for line in rf.readlines():
                if "PokerStars Hand" in line:
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

    def read_hand(self, hand, hand_regex):
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
                # get player name and number of chips
                line_list = line.split(" ")

                # get different pieces of data pre dealing
                seat_number = int(line_list[1].strip(":"))
                player_name = re.sub('[:\( ]', '', player[0])
                chips = line_list[-4].strip("($")  # THIS MAY BE A PROBLEM TEST

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

    def read_betting_action(self, lines_list):
        data = {}
        print("This should interpret the post deal lines")

        for line in lines_list:

            if "Dealt" in line:
                player_name = line.split()[2]
                # data["Player Name"].append(player_name)
                cards = [line.split()[3].lstrip("["), line.split()[4].rstrip("]")]
                print(player_name, cards)

            elif ":" in line:
                player_name = line.split(":")[0]
                action = line.split(":")[1].rstrip()
                if player_name not in data.keys():
                    data[player_name] = [action]
                else:
                    data[player_name].append(action)

                print(player_name, action)
        normalised_dict = dict([(k, pd.Series(v)) for k, v in data.items()])
        df = pd.DataFrame(normalised_dict).transpose()
        df.columns = [f"Post-Flop Action {i}" for i in range(1, len(df.columns) + 1)]
        return df

    def operations(self, operator, line):
        return {
            "showed": re.findall("\[.*\]", line)[0],
        }.get(operator, None)

    def read_summary(self, lines_list):
        data = {}
        for line in lines_list:
            if "showed" in line:
                a = line.split("showed")[0].rstrip("(button) ")
                b = re.sub("Seat [0-9]: ", "", a)
                data[b] = re.findall("\[.+]", line)[0].strip("[]")

        return pd.DataFrame(data.values(), index=data.keys(), columns=["Player Cards"])

    def read_pokerstars_file(self, lines):
        """
        A function that processes a pokerstars game and returns a dataframe with a summary of all events in game

        Args:
            file (str): file to read

        Returns:
            events df (pandas df)
        """

        data_dict = {}
        # process file
        chunks = self.split_game_to_events(file=None, lines=lines)

        # pre-deal data
        data_dict["pre_action"] = self.read_pre_deal_lines(chunks["HEADER"])

        search_dict = {"deal": "HOLE CARDS",
                       "flop": "FLOP",
                       "turn": "TURN",
                       "river": "RIVER",
                       "showdown": "SHOW DOWN"}

        for key, value in search_dict.items():
            try:
                data_dict[key] = self.read_betting_action(chunks[value])
            except KeyError:
                break

        data_dict["summary"] = self.read_summary(chunks["SUMMARY"])
        events_df = pd.concat([val for val in data_dict.values()], axis=1)
        return events_df


"""   dicts = {}
    process_file("../pokerstars/Multitest/HH20210210 Ornamenta V - $0.01-$0.02 - USD No Limit Hold'em.txt")
    for i in range(1, 50):
        try:
            dicts[i] = read_pokerstars_file(f"../pokerstars/Multitest/hand_{i}.txt")
        except FileNotFoundError:
            continue"""

# summary
# summ = read_pokerstars_file(f"../pokerstars/Multitest/hand_19.txt")
# summary = read_summary(summ["summary"].astype(str).values.tolist())
# merged_test = pd.merge(players_from_list, post_deal_data, left_index=True, right_index=True)
# print(plays)
# me, board = read_hand_file("../pokerstars/full_game_example.txt")
