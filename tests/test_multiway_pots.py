from src.poker_main import *


def test_always_passes():
    assert True


def test_heads_up_single_street_betting_single_winner_a():
    players = [

        Player("Abseil",
               chips=10,
               current_position="BB",
               pre_flop=["check"],
               post_flop=["raise to 5", "call"],
               cards=[Card("Ah")]),

        Player("Bobseil",
               chips=10,
               current_position="SB",
               pre_flop=["call"],
               cards=[Card("Kc")],
               post_flop=["check", "raise to 10"],
               turn=[],
               river=[]),

    ]

    table_cards = [Card("2h"), Card("2c"), Card("2s"), Card("2d"), Card("3h")]
    game = Poker(players, table_cards=table_cards)

    game.play_game()
    print(game.ranked_players)
    assert game.winners[0].name == "Abseil"
    assert game.ranked_players[0][0].chips == 20
    assert game.winners[0].chips == 20
    assert game.players[0].chips == 20


def test_heads_up_single_street_betting_single_winner_b():
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
    print(game.ranked_players)
    assert game.winners[0].name == "Bobseil"
    assert game.ranked_players[0][0].chips == 20
    assert game.winners[0].chips == 20
    assert game.players[1].chips == 20


class HeadsUpTests(object):
    pass
