from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

File = int   # 0-7
Rank = int   # 0-7
Square = Tuple[File, Rank]


class Color(str, Enum):
    WHITE = "white"
    BLACK = "black"

    @property
    def opposite(self) -> "Color":
        return Color.BLACK if self is Color.WHITE else Color.WHITE


class PieceType(str, Enum):
    PAWN = "pawn"
    ROOK = "rook"
    KNIGHT = "knight"
    BISHOP = "bishop"
    QUEEN = "queen"
    KING = "king"


@dataclass
class Piece:
    color: Color
    type: PieceType

    def symbol(self) -> str:
        base = {
            PieceType.PAWN: "p", PieceType.ROOK: "r", PieceType.KNIGHT: "n",
            PieceType.BISHOP: "b", PieceType.QUEEN: "q", PieceType.KING: "k",
        }[self.type]
        return base.upper() if self.color == Color.WHITE else base
