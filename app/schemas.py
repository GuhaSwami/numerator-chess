from pydantic import BaseModel, Field

PATTERN = r"^[a-h][1-8]$"           # algebraic square, e.g. a2, h7

class MoveAlgebraic(BaseModel):
    src: str = Field(..., pattern=PATTERN)
    dst: str = Field(..., pattern=PATTERN)