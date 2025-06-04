from app.game import Game

def test_simple_pawn_move():
    g = Game()
    # white pawn e2 -> e4
    assert g.move((4, 1), (4, 3))
    # black pawn e7 -> e5
    assert g.move((4, 6), (4, 4))
