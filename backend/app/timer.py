"""Backend-driven round timer.

The RoundDriver owns the *timing* of a game: it announces each round, waits
`round_seconds` (or until `signal_early_end` fires once everyone has
guessed), reveals the answer, advances, and finally announces the end —
emitting an event dict at each transition. The API layer turns those events
into WebSocket broadcasts.

`sleep` and `time_fn` are injected so tests can pass a no-op sleep and a
fixed clock and run instantly and deterministically. In production they're
`asyncio.sleep` and `time.time`.

The early-end wait is a plain poll loop (checking a flag between short
sleeps) rather than an `asyncio.Event` raced against the timeout: it needs
no extra task, no cancellation bookkeeping, and reuses the same injectable
`sleep` the rest of the driver already uses for its timing.
"""

from __future__ import annotations

import asyncio
import time
from typing import Awaitable, Callable, Dict

from app.game import advance_round, current_photo
from app.models import Room, RoomState

EventCallback = Callable[[Dict], None]
SleepFn = Callable[[float], Awaitable[None]]
TimeFn = Callable[[], float]

# How often the driver checks for an early-end signal while waiting out a
# round. Small enough to feel responsive, large enough to not busy-loop.
_POLL_INTERVAL = 0.2


class RoundDriver:
    def __init__(
        self,
        room: Room,
        *,
        sleep: SleepFn = asyncio.sleep,
        time_fn: TimeFn = time.time,
        on_event: EventCallback,
    ) -> None:
        self.room = room
        self._sleep = sleep
        self._time_fn = time_fn
        self._on_event = on_event
        self._early_end_round: int | None = None

    def _photo_dict(self) -> Dict:
        photo = current_photo(self.room)
        return {"id": photo.id, "owner_id": photo.owner_id, "url": photo.url}

    def signal_early_end(self, round_index: int) -> None:
        """Wake the driver early once every player has guessed.

        Ignored if `round_index` doesn't match the round currently being
        timed, guarding a race between a slow in-flight guess request and
        the round already having moved on via the normal timeout.
        """
        if round_index == self.room.current_round:
            self._early_end_round = round_index

    async def _wait_for_round(self, round_index: int, round_seconds: float) -> None:
        """Wait out the round, or return early once `signal_early_end` fires."""
        elapsed = 0.0
        while elapsed < round_seconds:
            step = min(_POLL_INTERVAL, round_seconds - elapsed)
            await self._sleep(step)
            elapsed += step
            if self._early_end_round == round_index:
                return

    async def run(self) -> None:
        """Drive the game from its first round to completion."""
        while self.room.state == RoomState.IN_ROUND:
            round_index = self.room.current_round
            round_seconds = self.room.round_seconds
            round_ends_at = int((self._time_fn() + round_seconds) * 1000)
            self._early_end_round = None

            self._on_event(
                {
                    "type": "round_started",
                    "round_index": round_index,
                    "photo": self._photo_dict(),
                    "round_ends_at": round_ends_at,
                }
            )

            await self._wait_for_round(round_index, round_seconds)

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
