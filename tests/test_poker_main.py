import pytest
from src.poker_main import Poker, Card, Player, BoardAnalysis


def test_four_of_a_kind():
    # four of a kind test
    players = [

        Player("a", chips=10, current_position="BTN", cards=[Card("A", "hearts")]),
        Player("b", chips=1000, current_position="SB", cards=[Card("K", "hearts")]),
        Player("c", chips=1000, current_position="BB", cards=[Card("Q", "hearts")]),

    ]
    table_cards = [Card("2", "clubs"), Card("2", "spades"), Card("2", "diamonds"), Card("2", "hearts")]
    analysis = BoardAnalysis(players, table_cards)

    assert analysis.winners_names[0] == "a"


def test_three_of_a_kind():
    # three of a kind test
    players = [

        Player("a", chips=10, current_position="BTN", cards=[Card("A", "hearts"), Card("K", "hearts")]),
        Player("b", chips=1000, current_position="SB", cards=[Card("K", "hearts"), Card("A", "diamonds")]),
        Player("c", chips=1000, current_position="BB", cards=[Card("Q", "hearts"), Card("A", "spades")]),

    ]
    table_cards = [Card("2", "clubs"), Card("2", "spades"), Card("2", "diamonds")]
    analysis = BoardAnalysis(players, table_cards)

    assert analysis.winners_names[0] == "a"
