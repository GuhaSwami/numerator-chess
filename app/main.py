from fastapi import FastAPI, HTTPException
from .storage import new_game, get_game
from .schemas import CreateGameResponse, MoveRequest, MoveResponse

app = FastAPI(title="Chess Game Service")


@app.post("/game", response_model=CreateGameResponse)
def create_game():
    g = new_game()
    return {"game_id": g.id, "board": g.board.ascii()}


@app.post("/game/{gid}/move", response_model=MoveResponse)
def make_move(gid: str, req: MoveRequest):
    g = get_game(gid)
    if not g:
        raise HTTPException(status_code=404, detail="game not found")
    ok = g.move(tuple(req.src), tuple(req.dst))
    if not ok:
        raise HTTPException(status_code=400, detail="illegal move")
    return {
        "ok": True,
        "board": g.board.ascii(),
        "turn": g.turn.value,
        "history": g.history,
    }
