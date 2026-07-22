"""Backend-driven round timer.

The RoundDriver owns the *timing* of a game: it announces each round, waits
`round_seconds`, reveals the answer, advances, and finally announces the end —
emitting an event dict at each transition. The API layer turns those events
into WebSocket broadcasts.

`sleep` is injected so tests can pass a no-op and run instantly (no real
waiting). In production it's `asyncio.sleep`.
"""

from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, Dict

from app.game import advance_round, current_photo
from app.models import Room, RoomState

EventCallback = Callable[[Dict], None]
SleepFn = Callable[[float], Awaitable[None]]


class RoundDriver:
    def __init__(
        self,
        room: Room,
        *,
        round_seconds: float = 10,
        sleep: SleepFn = asyncio.sleep,
        on_event: EventCallback,
    ) -> None:
        self.room = room
        self.round_seconds = round_seconds
        self._sleep = sleep
        self._on_event = on_event

    def _photo_dict(self) -> Dict:
        photo = current_photo(self.room)
        return {"id": photo.id, "owner_id": photo.owner_id, "url": photo.url}

    async def run(self) -> None:
        """Drive the game from its first round to completion."""
        while self.room.state == RoomState.IN_ROUND:
            round_index = self.room.current_round

            self._on_event(
                {
                    "type": "round_started",
                    "round_index": round_index,
                    "photo": self._photo_dict(),
                }
            )

            await self._sleep(self.round_seconds)

            owner_id = current_photo(self.room).owner_id
            self._on_event(
                {
                    "type": "round_revealed",
                    "round_index": round_index,
                    "owner_id": owner_id,
                }
            )

            advance_round(self.room)

        # Left the IN_ROUND loop -> the game is finished.
        from app.game import rankings  # local import avoids a cycle at module load

        self._on_event(
            {
                "type": "game_finished",
                "rankings": [
                    {"id": p.id, "name": p.name, "score": p.score, "is_host": p.is_host}
                    for p in rankings(self.room)
                ],
            }
        )
