import re

suits = {"c": "clubs", "s": "spades", "d": "diamonds", "h": "hearts"}
values = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}


def bobson_stats(file):
    with open(file) as rf:
        i = 0
        for line in rf.readlines():
            if line == "\n":
                i += 1
                print(i)


def process_file(file):
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

me, board = read_hand_file("../pokerstars/hand_0")

