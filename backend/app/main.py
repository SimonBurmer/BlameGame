"""FastAPI application: REST endpoints + WebSocket route.

Thin I/O layer over the tested game logic in app/game.py. Endpoints validate
input, call the game functions, persist uploaded files to disk, and broadcast
events to connected players.

Cloud-ready for Railway: CORS is open (the Flutter client calls cross-origin),
and when run directly it binds 0.0.0.0 on the PORT env var. State is in-memory,
so run only ONE instance.
"""

from __future__ import annotations

import asyncio
import os
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.connection import manager
from app.game import (
    GameError,
    add_photo,
    add_player,
    advance_round,
    current_photo,
    rankings,
    reset_room,
    start_game,
    submit_guess,
)
from app.models import Photo, Player, Room
from app.store import RoomNotFound, store
from app.timer import RoundDriver

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="PhotoRoulette API")

# Open CORS: the Flutter app (incl. web/dev) will call from another origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- request bodies ------------------------------------------------------

class JoinBody(BaseModel):
    name: str


class StartBody(BaseModel):
    host_id: str
    total_rounds: int = 5
    round_seconds: int = 10


class GuessBody(BaseModel):
    guesser_id: str
    guessed_owner_id: str
    seconds_left: int


class ResetBody(BaseModel):
    host_id: str


# --- serialization helpers ----------------------------------------------

def _player_dict(p: Player) -> dict:
    return {"id": p.id, "name": p.name, "score": p.score, "is_host": p.is_host}


def _photo_dict(photo: Photo) -> dict:
    return {"id": photo.id, "owner_id": photo.owner_id, "url": photo.url}


def _room_dict(room: Room) -> dict:
    return {
        "code": room.code,
        "state": room.state.value,
        "current_round": room.current_round,
        "total_rounds": len(room.rounds),
        "players": [_player_dict(p) for p in room.players],
    }


def _get_room(code: str) -> Room:
    try:
        return store.get_room(code)
    except RoomNotFound:
        raise HTTPException(status_code=404, detail="room not found")


# --- REST endpoints ------------------------------------------------------

@app.post("/rooms")
def create_room() -> dict:
    room = store.create_room()
    return {"code": room.code}


@app.post("/rooms/{code}/join")
async def join_room(code: str, body: JoinBody) -> dict:
    room = _get_room(code)
    try:
        player = add_player(room, body.name)
    except GameError as e:
        raise HTTPException(status_code=400, detail=str(e))
    await manager.broadcast(
        room.code, {"type": "player_joined", "player": _player_dict(player)}
    )
    return {"player_id": player.id, "is_host": player.is_host}


@app.post("/rooms/{code}/photos")
async def upload_photo(
    code: str,
    owner_id: str,
    file: UploadFile = File(...),
) -> dict:
    room = _get_room(code)
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail="file must be an image")

    room_dir = UPLOAD_DIR / room.code
    room_dir.mkdir(parents=True, exist_ok=True)
    photo_id = uuid.uuid4().hex[:12]
    dest = room_dir / f"{photo_id}.jpg"
    dest.write_bytes(await file.read())

    url = f"/rooms/{room.code}/photos/{photo_id}.jpg"
    try:
        photo = add_photo(room, owner_id=owner_id, url=url)
    except GameError as e:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(e))
    return {"photo_id": photo.id, "url": photo.url}


@app.get("/rooms/{code}/photos/{filename}")
def get_photo(code: str, filename: str) -> FileResponse:
    path = UPLOAD_DIR / code / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="photo not found")
    return FileResponse(path)


@app.get("/rooms/{code}")
def get_room(code: str) -> dict:
    return _room_dict(_get_room(code))


@app.post("/rooms/{code}/start")
async def start(code: str, body: StartBody) -> dict:
    room = _get_room(code)
    host = room.player_by_id(body.host_id)
    if host is None or not host.is_host:
        raise HTTPException(status_code=403, detail="only the host can start")
    try:
        start_game(room, total_rounds=body.total_rounds)
    except GameError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # The driver owns round timing: it broadcasts round_started, waits, reveals,
    # advances, and finishes — all over the WebSocket. Each sync on_event
    # schedules an async broadcast on the running loop.
    loop = asyncio.get_running_loop()

    def emit(event: dict) -> None:
        loop.create_task(manager.broadcast(room.code, event))

    driver = RoundDriver(room, round_seconds=body.round_seconds, on_event=emit)
    asyncio.create_task(driver.run())

    return _room_dict(room)


@app.post("/rooms/{code}/guess")
async def guess(code: str, body: GuessBody) -> dict:
    room = _get_room(code)
    try:
        points = submit_guess(
            room,
            guesser_id=body.guesser_id,
            guessed_owner_id=body.guessed_owner_id,
            seconds_left=body.seconds_left,
        )
    except GameError as e:
        raise HTTPException(status_code=400, detail=str(e))
    await manager.broadcast(
        room.code,
        {
            "type": "guess_result",
            "guesser_id": body.guesser_id,
            "points": points,
            "correct": points > 0,
        },
    )
    return {"points": points, "correct": points > 0}


@app.post("/rooms/{code}/advance")
async def advance(code: str) -> dict:
    room = _get_room(code)
    try:
        advance_round(room)
    except GameError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if room.state.value == "finished":
        await manager.broadcast(
            room.code,
            {
                "type": "game_finished",
                "rankings": [_player_dict(p) for p in rankings(room)],
            },
        )
    else:
        await _broadcast_round_started(room)
    return _room_dict(room)


@app.post("/rooms/{code}/reset")
async def reset(code: str, body: ResetBody) -> dict:
    room = _get_room(code)
    host = room.player_by_id(body.host_id)
    if host is None or not host.is_host:
        raise HTTPException(status_code=403, detail="only the host can reset the room")
    try:
        reset_room(room)
    except GameError as e:
        raise HTTPException(status_code=400, detail=str(e))
    await manager.broadcast(
        room.code,
        {"type": "room_reset", "players": [_player_dict(p) for p in room.players]},
    )
    return _room_dict(room)


async def _broadcast_round_started(room: Room) -> None:
    await manager.broadcast(
        room.code,
        {
            "type": "round_started",
            "round_index": room.current_round,
            "photo": _photo_dict(current_photo(room)),
        },
    )


# --- WebSocket -----------------------------------------------------------

@app.websocket("/ws/{code}/{player_id}")
async def game_socket(websocket: WebSocket, code: str, player_id: str) -> None:
    try:
        store.get_room(code)
    except RoomNotFound:
        await websocket.close(code=4004)
        return

    await manager.connect(code, websocket)
    try:
        while True:
            # We don't require inbound messages; keep the socket open so the
            # client can receive broadcasts. receive_text() blocks until the
            # client sends or disconnects.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(code, websocket)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
