from pydantic import BaseModel, Field
from typing import List, Tuple

Square = Tuple[int, int]


class CreateGameResponse(BaseModel):
    game_id: str
    board: str


class MoveRequest(BaseModel):
    src: Square = Field(..., example=[0, 1])
    dst: Square = Field(..., example=[0, 3])


class MoveResponse(BaseModel):
    ok: bool
    board: str
    turn: str
    history: List[str]
