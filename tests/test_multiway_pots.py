from src.poker_main import *
import pytest


def test_always_passes():
    assert True


@pytest.mark.parametrize("winner_cards, loser_cards", [

    # High card over High card (highest)
    (
            [Card("Ah")],
            [Card("Kh")]
    ),

    # High card over High card (lowest)
    (
            [Card("6h")],
            [Card("3c")]
    ),

    # Pair over pair (high)
    (
            [Card("Ah"), Card("Ac")],
            [Card("Kh"), Card("Kc")]
    ),
    # Pair over pair (lowest)
    (
            [Card("6h"), Card("6c")],
            [Card("3h"), Card("3c")]
    ),

    # two pair over two pair (2 different pairs)
    (
            [Card("Ah"), Card("Ac"), Card("9h")],
            [Card("3h"), Card("3c"), Card("7h")]),

    # two pair over two pair (1 pair same)
    (
            [Card("Ah"), Card("Ac"), Card("9h")],
            [Card("3h"), Card("3c"), Card("9h")]
    ),

    # two pair over two pair (one over pair + third pair)
    (
            [Card("Ah"), Card("Ac"), Card("8h")],
            [Card("Kh"), Card("Kc"), Card("9h")]
    ),

    # two pair over two pair (one over pair + fourth pair)
    (
            [Card("Ah"), Card("Ac"), Card("2h")],
            [Card("Kh"), Card("Kc"), Card("9h")]
    ),

    # set over set
    (
            [Card("Ah"), Card("Ac"), Card("As")],
            [Card("Kh"), Card("Kc"), Card("Ks")]),

    # set over set on board
    (
            [Card("Ah"), Card("Ac"), Card("As")],
            [Card("9h"), Card("9s")]
    ),

    # straight over straight
    (
            [Card("Ah"), Card("Kc"), Card("Qs"), Card("Jh"), Card("Td")],
            [Card("Kc"), Card("Qs"), Card("Jh"), Card("Td"), Card("9h")]
    ),

    # 2nd lowest straight over straight
    (
            [Card("2h"), Card("3c"), Card("4s"), Card("5h"), Card("6d")],
            [Card("Ac"), Card("2s"), Card("3h"), Card("4d"), Card("5h")]
    ),

    # A-high straight over A-low straight
    (
            [Card("Ah"), Card("Kc"), Card("Qs"), Card("Jh"), Card("Td")],
            [Card("Ac"), Card("2s"), Card("3h"), Card("4d"), Card("5h")]
    ),

    # flush over flush (high)
    (
            [Card("Ah"), Card("Kh"), Card("Jh"), Card("Th"), Card("9d")],
            [Card("Kc"), Card("Qc"), Card("Tc"), Card("9c"), Card("8c")]
    ),

    # flush over flush (low)
    (
            [Card("8s"), Card("6s"), Card("4s"), Card("3s"), Card("2s")],
            [Card("7c"), Card("6c"), Card("5c"), Card("3c"), Card("2c")]
    ),

    # boat over boat (pair over)
    (
            [Card("As"), Card("Ah"), Card("Ks"), Card("Kc"), Card("Kds")],
            [Card("Qc"), Card("Qh"), Card("Qs"), Card("Jd"), Card("Js")]
    ),

    # boat over boat (pair under)
    (
            [Card("Qs"), Card("Qh"), Card("As"), Card("Ac"), Card("As")],
            [Card("Ac"), Card("Ah"), Card("Ks"), Card("Kd"), Card("Ks")]
    ),

    # quads over quads
    (
            [Card("As"), Card("Ah"), Card("Ad"), Card("Ac")],
            [Card("Ks"), Card("Kh"), Card("Kd"), Card("Kc")],
    ),

    # straight flush over straight flush
    (
            [Card("Ks"), Card("Qs"), Card("Js"), Card("Ts"), Card("9s")],
            [Card("Qc"), Card("Jc"), Card("Tc"), Card("9c"), Card("8c")],
    ),

    # royal flush over straight flush
    (
            [Card("As"), Card("Ks"), Card("Qs"), Card("Js"), Card("Ts")],
            [Card("Kc"), Card("Qc"), Card("Jc"), Card("Tc"), Card("9c")],
    ),

    # high pair over high card (lowest)
    # high pair over high card (highest)
    # low pair over high card (lowest)
    # low pair over high card (highest)

    # highest two pair over high card (lowest)
    # highest two pair over high card (highest)
    # lowest two pair over high card (lowest)
    # lowest two pair over high card (highest)

    # highest two pair over high pair
    # highest two pair over high pair
    # lowest two pair over low pair
    # lowest two pair over low pair

    # high set over high card (lowest)
    # high set over high card (highest)
    # low set over high card (lowest)
    # low set over high card (highest)


])
def test_heads_up_single_street_betting_single_winner_a(winner_cards, loser_cards):
    players = [

        Player("A",
               chips=10,
               current_position="BB",
               pre_flop=["check"],
               post_flop=["raise to 5", "call"],
               cards=winner_cards),

        Player("B",
               chips=10,
               current_position="SB",
               pre_flop=["call"],
               cards=loser_cards,
               post_flop=["check", "raise to 10"],
               turn=[],
               river=[]),

    ]

    table_cards = [Card("2h"), Card("4c"), Card("5s"), Card("8d"), Card("9h")]
    game = Poker(players, table_cards=table_cards)

    game.play_game()

    assert game.winners[0].name == "A"
    assert game.ranked_players[0][0].chips == 20
    assert game.winners[0].chips == 20
    assert game.players[0].chips == 20


"""def test_heads_up_single_street_betting_single_winner_b():
    players = [

        Player("Abseil",
               chips=10,
               current_position="BB",
               pre_flop=["check"],
               post_flop=["raise to 5", "call"],
               cards=[Card("Kh")]),

        Player("Bobseil",
               chips=10,
               current_position="SB",
               pre_flop=["call"],
               cards=[Card("Ac")],
               post_flop=["check", "raise to 10"],
               turn=[],
               river=[]),

    ]

    table_cards = [Card("2h"), Card("2c"), Card("2s"), Card("2d"), Card("3h")]
    game = Poker(players, table_cards=table_cards)

    game.play_game()

    assert game.winners[0].name == "Bobseil"
    assert game.ranked_players[0][0].chips == 20
    assert game.winners[0].chips == 20
    assert game.players[1].chips == 20"""


class HeadsUpTests(object):
    pass
