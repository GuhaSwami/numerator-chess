from __future__ import annotations
from copy import deepcopy
from typing import List, Optional, Generator

from .models import Color, Piece, PieceType, Square

BOARD_SIZE = 8


class Board:
    """8×8 board.  (0,0) = a1; (7,7) = h8."""
    def __init__(self) -> None:
        self.grid: List[List[Optional[Piece]]] = [
            [None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)
        ]
        self._place_starting_pieces()

    # ─────────────────────────────────────────────────────────── Helpers
    def _place_starting_pieces(self) -> None:
        order = [
            PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
            PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK,
        ]
        for f in range(BOARD_SIZE):
            self.grid[f][0] = Piece(Color.WHITE, order[f])
            self.grid[f][1] = Piece(Color.WHITE, PieceType.PAWN)
            self.grid[f][6] = Piece(Color.BLACK, PieceType.PAWN)
            self.grid[f][7] = Piece(Color.BLACK, order[f])

    # ─────────────────────────────────────────────────────────── Query
    def piece_at(self, sq: Square) -> Optional[Piece]:
        f, r = sq
        return self.grid[f][r]

    def is_in_bounds(self, sq: Square) -> bool:
        f, r = sq
        return 0 <= f < BOARD_SIZE and 0 <= r < BOARD_SIZE

    # ─────────────────────────────────────────────────────────── Move-gen
    def generate_moves(self, sq: Square) -> List[Square]:
        """Legal moves for piece on *sq*.  (No full check-detection yet.)"""
        p = self.piece_at(sq)
        if not p:
            return []
        f, r = sq
        moves: List[Square] = []
        same_color = lambda s: self.piece_at(s) and self.piece_at(s).color == p.color
        add = lambda nf, nr: moves.append((nf, nr))

        if p.type == PieceType.PAWN:
            dir = 1 if p.color == Color.WHITE else -1
            one = (f, r + dir)
            if self.is_in_bounds(one) and not self.piece_at(one):
                add(*one)
                # 2-step
                two = (f, r + 2 * dir)
                start_rank = 1 if p.color == Color.WHITE else 6
                if r == start_rank and not self.piece_at(two):
                    add(*two)
            # captures
            for df in (-1, 1):
                tgt = (f + df, r + dir)
                if self.is_in_bounds(tgt) and self.piece_at(tgt) and not same_color(tgt):
                    add(*tgt)
        elif p.type == PieceType.KNIGHT:
            for df, dr in [
                (1, 2), (2, 1), (-1, 2), (-2, 1),
                (1, -2), (2, -1), (-1, -2), (-2, -1)
            ]:
                tgt = (f + df, r + dr)
                if self.is_in_bounds(tgt) and not same_color(tgt):
                    add(*tgt)
        elif p.type in {PieceType.ROOK, PieceType.BISHOP, PieceType.QUEEN}:
            lines = []
            if p.type in {PieceType.ROOK, PieceType.QUEEN}:
                lines += [(1, 0), (-1, 0), (0, 1), (0, -1)]
            if p.type in {PieceType.BISHOP, PieceType.QUEEN}:
                lines += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for df, dr in lines:
                nf, nr = f + df, r + dr
                while self.is_in_bounds((nf, nr)):
                    if self.piece_at((nf, nr)):
                        if not same_color((nf, nr)):
                            add(nf, nr)
                        break
                    add(nf, nr)
                    nf += df
                    nr += dr
        elif p.type == PieceType.KING:
            for df in (-1, 0, 1):
                for dr in (-1, 0, 1):
                    if df == dr == 0:
                        continue
                    tgt = (f + df, r + dr)
                    if self.is_in_bounds(tgt) and not same_color(tgt):
                        add(*tgt)
        return moves

    # ─────────────────────────────────────────────────────────── Mutations
    def move(self, src: Square, dst: Square) -> bool:
        p = self.piece_at(src)
        if not p or dst not in self.generate_moves(src):
            return False
        self.grid[dst[0]][dst[1]] = p
        self.grid[src[0]][src[1]] = None
        return True

    # ─────────────────────────────────────────────────────────── Debug
    def ascii(self) -> str:
        rows = []
        for r in reversed(range(BOARD_SIZE)):
            row = []
            for f in range(BOARD_SIZE):
                piece = self.grid[f][r]
                row.append(piece.symbol() if piece else ".")
            rows.append(" ".join(row))
        return "\n".join(rows)
