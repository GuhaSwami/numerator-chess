import uuid
from typing import List

from .board import Board
from .models import Color, Square


class GameStatus(str):
    IN_PROGRESS = "in_progress"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"


class Game:
    def __init__(self) -> None:
        self.id = str(uuid.uuid4())
        self.board = Board()
        self.turn = Color.WHITE
        self.status = GameStatus.IN_PROGRESS
        self.history: List[str] = []

    # ─────────────────────────────────────────────────────────── Moves
    def move(self, src: Square, dst: Square) -> bool:
        if self.status != GameStatus.IN_PROGRESS:
            return False
        moved = self.board.move(src, dst)
        if moved:
            self.history.append(f"{self.turn.value}:{src}->{dst}")
            self.turn = self.turn.opposite
            # TODO: detect check/checkmate here
        return moved
