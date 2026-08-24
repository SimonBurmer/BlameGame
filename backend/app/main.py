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
import json
import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.connection import manager
from app.game import (
    GameError,
    add_photo,
    add_player,
    remove_player,
    reset_room,
    set_settings,
    start_game,
    submit_guess,
)
from app.models import Player, Room, RoomState
from app.store import RoomNotFound, store
from app.timer import RoundDriver

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Uploads are full-resolution camera-roll originals, so the cap is generous;
# without one, a single request reads unbounded bytes into memory.
MAX_PHOTO_BYTES = 8 * 1024 * 1024
_UPLOAD_CHUNK = 64 * 1024

# Background tasks are kept referenced: asyncio only holds a weak reference, so
# an unreferenced task can be garbage-collected mid-flight, and a task that
# raises otherwise fails silently.
_background_tasks: set[asyncio.Task] = set()

logger = logging.getLogger(__name__)


def _delete_room_uploads(code: str) -> None:
    """Delete one room's upload directory, and nothing else.

    Deleting a tree is destructive, so the target is re-derived from the room
    code and checked to be a direct child of UPLOAD_DIR: a code containing
    `..` or a separator resolves outside it and is refused rather than
    recursively removing whatever it happens to point at.
    """
    base = UPLOAD_DIR.resolve()
    room_dir = (base / code).resolve()
    if room_dir.parent != base:
        logger.error("refusing to delete uploads outside %s: %r", base, code)
        return
    shutil.rmtree(room_dir, ignore_errors=True)


store.on_evict = _delete_room_uploads


def _spawn(coro) -> None:
    task = asyncio.ensure_future(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    task.add_done_callback(_log_task_failure)


def _log_task_failure(task: asyncio.Task) -> None:
    if task.cancelled():
        return
    exc = task.exception()
    if exc is not None:
        logger.error("background task failed", exc_info=exc)


async def _read_capped(file: UploadFile) -> bytes:
    """Read an upload, refusing anything over MAX_PHOTO_BYTES."""
    chunks: list[bytes] = []
    total = 0
    while chunk := await file.read(_UPLOAD_CHUNK):
        total += len(chunk)
        if total > MAX_PHOTO_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"file too large (max {MAX_PHOTO_BYTES // (1024 * 1024)} MB)",
            )
        chunks.append(chunk)
    if not chunks:
        raise HTTPException(status_code=400, detail="empty file")
    return b"".join(chunks)

app = FastAPI(title="Blame Game API")

# Open CORS: the Flutter app (incl. web/dev) will call from another origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # No cookies or Authorization headers are used, and "*" + credentials
    # makes Starlette reflect any requesting origin.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- request bodies ------------------------------------------------------

class CreateRoomBody(BaseModel):
    # Optional starting value; the host sets the mode in the lobby now, and
    # the client no longer sends this.
    hardcore: bool = False


class SettingsBody(BaseModel):
    host_id: str
    # All optional so a client can change one setting without restating the
    # rest. Bounds match StartBody: these are HTTP inputs, so out-of-range is a
    # 422 at the boundary rather than a game rule.
    total_rounds: Optional[int] = Field(default=None, ge=1, le=50)
    round_seconds: Optional[int] = Field(default=None, ge=1, le=120)
    hardcore: Optional[bool] = None


class JoinBody(BaseModel):
    name: str = Field(min_length=1, max_length=24)


class StartBody(BaseModel):
    host_id: str
    # Bounded here rather than in game.py: these are HTTP inputs, so an
    # out-of-range value is a 422 at the boundary, not a game rule. Omitted
    # means "use what the host configured in the lobby".
    total_rounds: Optional[int] = Field(default=None, ge=1, le=50)
    round_seconds: Optional[int] = Field(default=None, ge=1, le=120)


class GuessBody(BaseModel):
    guesser_id: str
    guessed_owner_id: str
    # The round the client believed it was answering. Optional so an older
    # client still works; when present it guards the round-rollover race.
    round_index: Optional[int] = None


class ResetBody(BaseModel):
    host_id: str


class LeaveBody(BaseModel):
    player_id: str


class KickBody(BaseModel):
    host_id: str
    player_id: str


# --- serialization helpers ----------------------------------------------

def _player_dict(p: Player, room: Room | None = None) -> dict:
    d = {"id": p.id, "name": p.name, "score": p.score, "is_host": p.is_host}
    if room is not None:
        # Lets the lobby show who has actually contributed photos, instead of
        # a decorative tick that always reads "ready".
        d["photo_count"] = sum(1 for photo in room.photos if photo.owner_id == p.id)
    return d


def _room_dict(room: Room, player_id: str | None = None) -> dict:
    d = {
        "code": room.code,
        "state": room.state.value,
        "current_round": room.current_round,
        # Before the game starts there are no rounds yet, so report the host's
        # configured length; once it is running the built rounds are the truth.
        "total_rounds": len(room.rounds) or room.total_rounds,
        "round_seconds": room.round_seconds,
        "hardcore": room.hardcore,
        "players": [_player_dict(p, room) for p in room.players],
    }
    if room.rounds and room.state is not RoomState.LOBBY:
        rnd = room.rounds[room.current_round]
        revealed = room.state is not RoomState.IN_ROUND
        photo = {"id": rnd.photo.id, "url": rnd.photo.url}
        # The owner is the answer players are guessing, so it is withheld while
        # the round is live — matching round_revealed, which is the first event
        # that discloses it. A reconnecting client that got it here would be
        # handed a free correct guess.
        if revealed:
            photo["owner_id"] = rnd.photo.owner_id
        d["round"] = {
            "index": rnd.index,
            "photo": photo,
            # Epoch ms, same units and same server authority as round_started;
            # the client derives remaining time as this minus now().
            "ends_at": None if revealed or rnd.ends_at is None else int(rnd.ends_at * 1000),
            # So a player who already guessed this round before dropping out
            # doesn't come back with a fresh guess (the server would reject it
            # anyway; this keeps the UI honest instead of offering the button).
            "has_guessed": player_id is not None and player_id in rnd.guesses,
        }
    return d


def _get_room(code: str) -> Room:
    try:
        return store.get_room(code)
    except RoomNotFound:
        raise HTTPException(status_code=404, detail="room not found")


# --- REST endpoints ------------------------------------------------------

@app.post("/rooms")
def create_room(body: CreateRoomBody | None = None) -> dict:
    # Body is optional so a client that posts nothing still gets a normal room.
    room = store.create_room(hardcore=bool(body and body.hardcore))
    return {"code": room.code, "hardcore": room.hardcore}


@app.post("/rooms/{code}/join")
async def join_room(code: str, body: JoinBody) -> dict:
    room = _get_room(code)
    try:
        player = add_player(room, body.name)
    except GameError as e:
        raise HTTPException(status_code=400, detail=str(e))
    await manager.broadcast(
        room.code, {"type": "player_joined", "player": _player_dict(player, room)}
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

    data = await _read_capped(file)
    # Trust the bytes, not the client's content-type header -- that also means
    # the extension we store comes from the bytes, so a PNG isn't served as
    # a .jpg and decoded by whatever the client guesses.
    if data.startswith(b"\xff\xd8\xff"):
        ext = "jpg"
    elif data.startswith(b"\x89PNG\r\n\x1a\n"):
        ext = "png"
    else:
        raise HTTPException(status_code=400, detail="file must be a JPEG or PNG")

    # Register the photo before writing it, so a rejected upload never leaves
    # an orphan file on disk.
    photo_id = uuid.uuid4().hex[:12]
    url = f"/rooms/{room.code}/photos/{photo_id}.{ext}"
    try:
        photo = add_photo(room, owner_id=owner_id, url=url)
    except GameError as e:
        raise HTTPException(status_code=400, detail=str(e))

    room_dir = UPLOAD_DIR / room.code
    room_dir.mkdir(parents=True, exist_ok=True)
    (room_dir / f"{photo_id}.{ext}").write_bytes(data)

    # Tell the lobby who is ready, so the host isn't guessing.
    await manager.broadcast(
        room.code,
        {
            "type": "photos_updated",
            "players": [_player_dict(p, room) for p in room.players],
        },
    )
    return {"photo_id": photo.id, "url": photo.url}


@app.get("/rooms/{code}/photos/{filename}")
def get_photo(code: str, filename: str) -> FileResponse:
    # `code` and `filename` are raw path params, so resolve the candidate and
    # confirm it stays inside UPLOAD_DIR: without this, `/rooms/../photos/x`
    # escapes the upload tree and serves arbitrary files from the working dir.
    base = UPLOAD_DIR.resolve()
    path = (base / code / filename).resolve()
    if not path.is_relative_to(base) or not path.is_file():
        raise HTTPException(status_code=404, detail="photo not found")
    return FileResponse(path)


@app.get("/rooms/{code}")
def get_room(code: str, player_id: str | None = None) -> dict:
    # player_id is optional and only scopes the caller's own view (whether they
    # already guessed this round). It grants nothing, so an absent or bogus one
    # simply means "no per-player detail".
    return _room_dict(_get_room(code), player_id)


@app.post("/rooms/{code}/settings")
async def update_settings(code: str, body: SettingsBody) -> dict:
    room = _get_room(code)
    host = room.player_by_id(body.host_id)
    if host is None or not host.is_host:
        raise HTTPException(status_code=403, detail="only the host can change settings")
    try:
        set_settings(
            room,
            total_rounds=body.total_rounds,
            round_seconds=body.round_seconds,
            hardcore=body.hardcore,
        )
    except GameError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # Non-hosts need to see what they are about to play, so the whole room gets
    # the new settings rather than only the host's own screen.
    await manager.broadcast(
        room.code,
        {
            "type": "settings_updated",
            "total_rounds": room.total_rounds,
            "round_seconds": room.round_seconds,
            "hardcore": room.hardcore,
        },
    )
    return _room_dict(room)


@app.post("/rooms/{code}/start")
async def start(code: str, body: StartBody) -> dict:
    room = _get_room(code)
    host = room.player_by_id(body.host_id)
    if host is None or not host.is_host:
        raise HTTPException(status_code=403, detail="only the host can start")
    try:
        start_game(
            room,
            total_rounds=body.total_rounds
            if body.total_rounds is not None
            else room.total_rounds,
            round_seconds=body.round_seconds
            if body.round_seconds is not None
            else room.round_seconds,
        )
    except GameError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # The driver owns round timing: it broadcasts round_started, waits, reveals,
    # advances, and finishes — all over the WebSocket. Each sync on_event
    # schedules an async broadcast on the running loop.
    def emit(event: dict) -> None:
        _spawn(manager.broadcast(room.code, event))

    driver = RoundDriver(room, on_event=emit)
    _spawn(driver.run())

    return _room_dict(room)


@app.post("/rooms/{code}/guess")
async def guess(code: str, body: GuessBody) -> dict:
    room = _get_room(code)
    try:
        points = submit_guess(
            room,
            guesser_id=body.guesser_id,
            guessed_owner_id=body.guessed_owner_id,
            round_index=body.round_index,
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


async def _remove_and_broadcast(room: Room, player_id: str, *, kicked: bool) -> dict:
    """Drop a player and tell the room. Shared by leaving and being kicked."""
    try:
        remove_player(room, player_id)
    except GameError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # One event for both: clients need the same reaction either way, and
    # `kicked` lets the removed player's own client say why it was ejected.
    await manager.broadcast(
        room.code,
        {
            "type": "player_left",
            "player_id": player_id,
            "kicked": kicked,
            "players": [_player_dict(p, room) for p in room.players],
        },
    )
    if kicked:
        # After the broadcast, so the kicked client still gets told why — but
        # not dependent on it reacting: the feed carries every photo URL, so
        # the server closes their socket itself.
        await manager.close_player(room.code, player_id)
    return _room_dict(room)


@app.post("/rooms/{code}/leave")
async def leave(code: str, body: LeaveBody) -> dict:
    room = _get_room(code)
    return await _remove_and_broadcast(room, body.player_id, kicked=False)


@app.post("/rooms/{code}/kick")
async def kick(code: str, body: KickBody) -> dict:
    room = _get_room(code)
    host = room.player_by_id(body.host_id)
    if host is None or not host.is_host:
        raise HTTPException(status_code=403, detail="only the host can kick")
    if body.player_id == body.host_id:
        raise HTTPException(status_code=400, detail="the host cannot kick themselves")
    return await _remove_and_broadcast(room, body.player_id, kicked=True)


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
        {
            "type": "room_reset",
            "players": [_player_dict(p, room) for p in room.players],
        },
    )
    return _room_dict(room)


@app.delete("/rooms/{code}")
async def end_room(code: str, host_id: str) -> dict:
    room = _get_room(code)
    host = room.player_by_id(host_id)
    if host is None or not host.is_host:
        raise HTTPException(status_code=403, detail="only the host can end the room")
    # Tell everyone before the room is gone: after the delete there is no room
    # to broadcast to, and clients would just see their socket drop.
    await manager.broadcast(room.code, {"type": "room_closed"})
    store.delete_room(room.code)
    return {"code": room.code, "deleted": True}


# --- WebSocket -----------------------------------------------------------

@app.websocket("/ws/{code}/{player_id}")
async def game_socket(websocket: WebSocket, code: str, player_id: str) -> None:
    try:
        room = store.get_room(code)
    except RoomNotFound:
        await websocket.close(code=4004)
        return

    # Only players of this room get the feed: the stream carries every photo
    # URL in the game.
    if room.player_by_id(player_id) is None:
        await websocket.close(code=4003)
        return

    # Register under the room's canonical code. The path param is whatever the
    # client typed, and broadcasts target room.code -- registering under a
    # lowercase code produced a socket that connected fine and then silently
    # received nothing, forever.
    await manager.connect(room.code, player_id, websocket)
    try:
        while True:
            # We don't require inbound messages; keep the socket open so the
            # client can receive broadcasts. receive_text() blocks until the
            # client sends or disconnects.
            message = await websocket.receive_text()
            # Answer heartbeats. A silently dropped connection delivers no
            # close frame on mobile, so the client can only tell the socket is
            # dead by noticing this reply never arrives. Anything else inbound
            # is ignored -- a garbage frame must not kill a player's feed.
            try:
                if json.loads(message).get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except (ValueError, AttributeError):
                pass
    except WebSocketDisconnect:
        pass
    finally:
        # finally, not just the disconnect branch: server shutdown or a
        # cancellation would otherwise leak the socket in the room registry.
        manager.disconnect(room.code, websocket)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
