"""WebSocket connection management and per-room broadcasting.

Each connected player holds one WebSocket. When something happens in a room
(a player joins, a round starts, the game finishes) we broadcast a JSON event
to every socket currently connected to that room.
"""

from __future__ import annotations

import asyncio
from typing import Dict, List

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        # room code -> list of live sockets
        self._rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, room_code: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._rooms.setdefault(room_code, []).append(websocket)

    def disconnect(self, room_code: str, websocket: WebSocket) -> None:
        sockets = self._rooms.get(room_code)
        if sockets and websocket in sockets:
            sockets.remove(websocket)
        if sockets is not None and not sockets:
            self._rooms.pop(room_code, None)

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
