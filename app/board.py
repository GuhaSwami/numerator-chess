from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

class Color(str, Enum):
    # Side to move / piece ownership.
    WHITE = "w"
    BLACK = "b"

    def other(self) -> "Color":
        return Color.BLACK if self is Color.WHITE else Color.WHITE # Return the opposite color - used after a successful move.


Square = Tuple[int, int]  # Board coordinates (file 0-7, rank 0-7)

@dataclass(frozen=True)
class _MoveSpec:
    vectors: Tuple[Tuple[int, int], ...] # vectors - relative (dx, dy) steps
    slide: bool # slide   - if True, piece may repeat the travelling line until blocked


# Movement definitions keyed by piece letter
MOVE_TABLE = {
    "P": _MoveSpec(((0, 1),), False),  # Pawns are handled in a custom helper
    "N": _MoveSpec(                   # Knight L-shapes (non-sliding)
        ((1, 2), (2, 1), (-1, 2), (-2, 1),
         (1, -2), (2, -1), (-1, -2), (-2, -1)),
        False,
    ),
    "B": _MoveSpec(((1, 1), (-1, 1), (1, -1), (-1, -1)), True),  # Diagonals
    "R": _MoveSpec(((1, 0), (-1, 0), (0, 1), (0, -1)), True),    # Files/ranks
    "Q": _MoveSpec(((1, 1), (-1, 1), (1, -1), (-1, -1),          # Bishop + Rook
                    (1, 0), (-1, 0), (0, 1), (0, -1)), True),
    "K": _MoveSpec(((1, 1), (-1, 1), (1, -1), (-1, -1),          # One-square
                    (1, 0), (-1, 0), (0, 1), (0, -1)), False),
}

# CHATGPT Prompt: In Python, create a dictionary that maps each chess-piece letter to a MoveSpec (I pasted the class here) describing its move vectors and whether the piece moves until blocked. Include entries for pawns, knights, bishops, rooks, queens, and kings.

@dataclass
class Piece:
    # piece label
    kind: str          # One of "PNBRQK"
    color: Color

    def __repr__(self) -> str:
        """Single-letter, lower-case for black, upper-case for white."""
        return self.kind if self.color is Color.WHITE else self.kind.lower()

# ──────────────────────── board engine ────────────────────────
class Board:

    def __init__(self) -> None:
        # 2-D grid: g[file][rank]
        self.g: List[List[Optional[Piece]]] = [[None] * 8 for _ in range(8)]
        self.turn: Color = Color.WHITE

        # Initial layout
        order = "RNBQKBNR"
        for f, k in enumerate(order):
            self.g[f][0] = Piece(k, Color.WHITE)
            self.g[f][7] = Piece(k, Color.BLACK)
            self.g[f][1] = Piece("P", Color.WHITE)
            self.g[f][6] = Piece("P", Color.BLACK)

    # ───────────── public API ─────────────
    def move(self, uci: str) -> None:
        # _alg2sq -> turn algebraic square name into tuple
        src, dst = map(self._alg2sq, (uci[:2], uci[2:]))
        piece = self._at(src)

        # --- basic validations ------------------------------------------------
        if not piece or piece.color != self.turn:
            raise ValueError("wrong turn")
        if dst not in self._legal_from(src):
            raise ValueError("illegal")

        # --- if an enemy peice is in that spot, it is deleted from the grid ---------------------------------------------------
        self._set(dst, piece)
        self._set(src, None)
        self.turn = self.turn.other()

    # ───────────── move generation ─────────────
    def _legal_from(self, sq: Square) -> List[Square]:
        """Return pseudo-legal target squares for the piece on *sq*."""
        p = self._at(sq)
        if not p:
            return []

        # Pawn rules diverge, everything else table-driven
        return (
            self._pawn_moves(sq, p.color)
            if p.kind == "P"
            else self._ray_moves(sq, MOVE_TABLE[p.kind])
        )

    def _ray_moves(self, sq: Square, spec: _MoveSpec) -> List[Square]:
        """
        Apply the given *spec* to generate rook/bishop/queen/knight/king moves.

        Repeats a vector until:
          * it hits the edge,
          * it bumps into a friendly piece (stop),
          * it captures an enemy piece (include square then stop),
          * or the spec is non-sliding (king/knight).
        """
        moves, src_piece = [], self._at(sq)
        for dx, dy in spec.vectors:
            cur = self._step(sq, (dx, dy))
            while cur:
                tgt = self._at(cur)
                if tgt and tgt.color == src_piece.color:
                    break               # blocked by friendly
                moves.append(cur)
                if tgt or not spec.slide:
                    break               # capture or non-slider: stop ray
                cur = self._step(cur, (dx, dy))
        return moves

    def _pawn_moves(self, sq: Square, col: Color) -> List[Square]:
        """
        Pawn logic: forward push (1 or 2 squares from start) + diagonal captures.
        """
        f, r = sq
        dir_ = 1 if col is Color.WHITE else -1  # White moves up (rank +1)

        moves, one = [], self._step(sq, (0, dir_))
        if one and not self._at(one):           # empty square ahead
            moves.append(one)

            # two-square jump from starting rank
            start = 1 if col is Color.WHITE else 6
            two = self._step(sq, (0, 2 * dir_))
            if r == start and two and not self._at(two):
                moves.append(two)

        # diagonal captures
        for df in (-1, 1):
            cap = self._step(sq, (df, dir_))
            if cap and (t := self._at(cap)) and t.color != col:
                moves.append(cap)

        return moves

    # ───────────── low-level helpers ─────────────
    def _at(self, s: Square) -> Optional[Piece]:
        """Return the piece on *s* or None."""
        return self.g[s[0]][s[1]]

    def _set(self, s: Square, p: Optional[Piece]) -> None:
        """Place *p* on *s* (or clear if None)."""
        self.g[s[0]][s[1]] = p

    def _step(self, s: Square, v: Tuple[int, int]) -> Optional[Square]:
        """
        Move one vector step from *s*.
        Returns new square if still on board, else ``None``.
        """
        nx = (s[0] + v[0], s[1] + v[1])
        return nx if 0 <= nx[0] < 8 and 0 <= nx[1] < 8 else None

    @staticmethod
    def _alg2sq(a: str) -> Square:
        """Algebraic 'e4' → internal (4, 3)."""
        return (ord(a[0]) - 97, int(a[1]) - 1)
