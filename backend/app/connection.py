"""WebSocket connection management and per-room broadcasting.

Each connected player holds one WebSocket. When something happens in a room
(a player joins, a round starts, the game finishes) we broadcast a JSON event
to every socket currently connected to that room.
"""

from __future__ import annotations

import asyncio
from typing import Dict, List, Tuple

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        # room code -> list of live sockets
        self._rooms: Dict[str, List[WebSocket]] = {}
        # (room code, player id) -> that player's live sockets. A list, not one
        # socket: a reconnect race can leave a stale socket open alongside the
        # new one, and closing "the" socket has to close both.
        self._players: Dict[Tuple[str, str], List[WebSocket]] = {}

    async def connect(self, room_code: str, player_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._rooms.setdefault(room_code, []).append(websocket)
        self._players.setdefault((room_code, player_id), []).append(websocket)

    def disconnect(self, room_code: str, websocket: WebSocket) -> None:
        sockets = self._rooms.get(room_code)
        if sockets and websocket in sockets:
            sockets.remove(websocket)
        if sockets is not None and not sockets:
            self._rooms.pop(room_code, None)
        for key, player_sockets in list(self._players.items()):
            if key[0] == room_code and websocket in player_sockets:
                player_sockets.remove(websocket)
                if not player_sockets:
                    self._players.pop(key, None)

    async def close_player(self, room_code: str, player_id: str, code: int = 4003) -> None:
        """Close every socket a player holds in this room, server-side.

        Kicking someone must stop their feed whether or not their client reacts
        to `player_left` — the feed carries every photo URL in the room. Errors
        are swallowed the way broadcast does: a socket that is already dead
        just needs unregistering.
        """
        for ws in list(self._players.get((room_code, player_id), [])):
            try:
                await ws.close(code=code)
            except Exception:  # noqa: BLE001 - already-dead socket
                pass
            self.disconnect(room_code, ws)

    async def broadcast(self, room_code: str, message: dict) -> None:
        """Send a JSON message to every socket connected to the room.

        Sends run concurrently: sequentially, one slow client would hold up
        everyone else's events, and rounds are timed, so a stalled peer would
        eat other players' round time. Dead sockets are cleaned up rather than
        crashing the send.
        """
        sockets = list(self._rooms.get(room_code, []))
        if not sockets:
            return
        results = await asyncio.gather(
            *(ws.send_json(message) for ws in sockets),
            return_exceptions=True,
        )
        for ws, result in zip(sockets, results):
            if isinstance(result, BaseException):
                self.disconnect(room_code, ws)


# Process-wide singleton used by the API layer.
manager = ConnectionManager()
