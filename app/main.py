from fastapi import FastAPI, HTTPException
from app.schemas import MoveAlgebraic
from app.storage import new_game, get_game   # ← the real helpers

app = FastAPI(title="Numerator Chess")

# ───────────────────────── create game ─────────────────────────
@app.post("/game")
def create_game():
    game = new_game()                 # returns Game instance + stores it
    return {"id": game.id, "board": str(game.board)}

# ───────────────────────── make a move ─────────────────────────
@app.post("/game/{gid}/move")
def play_move(gid: str, move: MoveAlgebraic):
    try:
        game = get_game(gid)          # raises KeyError if unknown id
    except KeyError:
        raise HTTPException(status_code=404, detail="game not found")

    try:
        game.board.move(move.src + move.dst)   # "a2a3", "e7e5", …
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"board": str(game.board)}

# URL to access swagger UI: http://127.0.0.1:8000/docs
