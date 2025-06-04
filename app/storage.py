from typing import Dict
from .game import Game

_games: Dict[str, Game] = {}


def new_game() -> Game:
    g = Game()
    _games[g.id] = g
    return g


def get_game(gid: str) -> Game | None:
    return _games.get(gid)
