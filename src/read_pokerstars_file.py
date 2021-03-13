import re
import pandas as pd

suits = {"c": "clubs", "s": "spades", "d": "diamonds", "h": "hearts"}
values = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}


def process_file(file):
    # a function that chunks a file of poker stars hand into individual games
    file_number = 0
    with open(file, "r") as rf:

        line_marker = 0
        write = False
        start = False
        for line in rf.readlines():

            if "***********" in line:
                start = True
                wf = open(f"../pokerstars/hand_{file_number}", "w")
                write = True

            if start:
                if write:
                    wf.write(line)

                if line == "\n":
                    line_marker += 1

                if line_marker == 2:
                    line_marker = 0
                    write = False
                    wf.close()
                    file_number += 1


def read_hand(hand, hand_regex):
    hand = hand_regex.findall(hand)[0].strip("[]").split()
    return hand


def translate_hand(hand):
    # translates hands from pokerstars output format to python readable list of tuples
    print(hand)
    translated_cards = []
    for card in hand:
        new_card = (values[card[0]], suits[card[1]])
        translated_cards.append(new_card)

    return translated_cards


def read_hand_file(file):
    # define regex for later
    hand_regex = re.compile("\[.*\]")

    with open(file, "r") as rf:
        for line in rf.readlines():
            if "Dealt" in line:
                hand = read_hand(line, hand_regex)
                translated_hand = translate_hand(hand)
            if "Board" in line:
                board = read_hand(line, hand_regex)
                translated_board = translate_hand(board)

    return translated_hand, translated_board


def get_button_seat(file):
    with open(file, "r") as rf:
        return int(re.search("#\d", rf.readlines()[1]).group().strip("#"))


def chunk_data(file):
    # TODO: I want to split data to pre-deal, pre-flop, post-flop, post-turn, post-river, showdown
    data_dicts = {}
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


def read_pre_deal_lines(player_list):
    data_dict = {"Player Name": [],
                 "Seat Number": [],
                 "Chips": []}
    button_seat = int(re.search("#\d", player_list[1]).group().strip("#"))
    print(button_seat)
    for line in player_list:
        player = re.findall(":.*\(", line)
        if player and "chips" in line:
            # get player name and chip number
            line_list = line.split(" ")

            # get different pieces of data pre dealing
            seat_number = int(line_list[1].strip(":"))
            player_name = re.sub('[:\( ]', '', player[0])
            chips = line_list[-4].strip("(").strip("$")
            data_dict["Player Name"].append(player_name)
            data_dict["Seat Number"].append(seat_number)
            data_dict["Chips"].append(chips)

    # renumber set numbers for ordering of play
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
    return data_df


def read_betting_action(lines_list):
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


def read_showdown(lines_list):
    data = {}
    print("This should read showdown data in")

    for line in lines_list:
        print(line.rstrip())


def read_summary(lines_list):
    data = {}
    print("This should read showdown data in")

    for line in lines_list:
        if any(i in line for i in ["won", "lost"]):
            print(line.rstrip())


def read_file(file):
    # reads in all data from a game on pokerstars and reduces it to a dataframe of info
    with open(file, "r") as rf:
        chunks = chunk_data(rf)

    # pre-deal data
    pre_deal_df = read_pre_deal_lines(chunks["HEADER"])  # if no lines should return nothing... speed problem later?

    # TODO: post deal actions
    #  post_deal_df = read_post_deal_lines(chunks["HOLE CARDS"])

    # TODO: post-flop actions
    #  post_flop_df = read_post_flop_lines(chunks["FLOP"])

    # TODO: post-turn actions
    #  post_turn_df = read_post_turn_lines(chunks["TURN"])

    # TODO: post-river actions
    #  post_turn_df = read_post_river_lines(chunks["RIVER"])

    # showdown
    # showdown_df = read_showdown_lines)chunks["SHOWDOWN"]


chunked_data = chunk_data("../pokerstars/full_game_example_2.txt")

# players_from_file = get_all_players_from_file("../pokerstars/full_game_example.txt")
# pre deal
# players_from_list = read_pre_deal_lines(chunked_data["HEADER"])

# post deal
# post_deal_data = read_post_deal_lines(chunked_data["HOLE CARDS"])

# post_flop
# post_flop_data = read_betting_action(chunked_data["FLOP"])

# showdown
# showdown_data = read_showdown(chunked_data["SHOW DOWN"])

# summary
# summary = read_summary(chunked_data["SUMMARY"])
# merged_test = pd.merge(players_from_list, post_deal_data, left_index=True, right_index=True)
# print(plays)
# me, board = read_hand_file("../pokerstars/full_game_example.txt")
