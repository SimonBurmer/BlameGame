"""In-memory store of active game rooms.

A single `GameStore` instance holds every room in a dict. State lives only in
RAM: it is lost on server restart, which is acceptable for short-lived party
games. Because it is in-memory, the backend must run as a SINGLE instance
(no horizontal scaling) — replicas would not share this dict.

Rooms are evicted after `ROOM_TTL_SECONDS` of inactivity. The sweep is lazy —
it runs on room create/lookup rather than on a background task — because the
only thing that grows the store is a request, so there is nothing to clean up
while the process is idle. `time_fn` and `on_evict` are injected the way
`timer.py` injects its clock, so tests run instantly and without touching disk.
"""

from __future__ import annotations

import random
import time
from typing import Callable, Dict, Optional

from app.models import Room

# Generous: a game is minutes long, but a lobby can sit while people join, and
# evicting a room out from under live players is worse than holding some RAM.
ROOM_TTL_SECONDS = 6 * 60 * 60

EvictCallback = Callable[[str], None]
TimeFn = Callable[[], float]

# Ambiguous characters (0/O, 1/I) left out so codes are easy to read aloud.
_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
_CODE_LENGTH = 5


class RoomNotFound(Exception):
    """Raised when a room code does not exist."""


class GameStore:
    def __init__(
        self,
        *,
        ttl_seconds: float = ROOM_TTL_SECONDS,
        time_fn: TimeFn = time.time,
        on_evict: Optional[EvictCallback] = None,
    ) -> None:
        self._rooms: Dict[str, Room] = {}
        self._ttl = ttl_seconds
        self._time_fn = time_fn
        self.on_evict = on_evict

    def sweep(self) -> list[str]:
        """Drop rooms idle for longer than the TTL. Returns the codes dropped."""
        cutoff = self._time_fn() - self._ttl
        stale = [c for c, r in self._rooms.items() if r.last_active < cutoff]
        for code in stale:
            self.delete_room(code)
        return stale

    def delete_room(self, code: str) -> None:
        """Remove a room and let the caller clean up whatever it owns on disk."""
        code = code.upper()
        if self._rooms.pop(code, None) is None:
            raise RoomNotFound(code)
        if self.on_evict is not None:
            self.on_evict(code)

    def _generate_code(self) -> str:
        while True:
            code = "".join(random.choices(_CODE_ALPHABET, k=_CODE_LENGTH))
            if code not in self._rooms:
                return code

    def create_room(self) -> Room:
        self.sweep()
        code = self._generate_code()
        room = Room(code=code, last_active=self._time_fn())
        self._rooms[code] = room
        return room

    def get_room(self, code: str) -> Room:
        self.sweep()
        code = code.upper()
        if code not in self._rooms:
            raise RoomNotFound(code)
        room = self._rooms[code]
        # Any lookup counts as activity: every request path goes through here,
        # so a room with players in it never ages out underneath them.
        room.last_active = self._time_fn()
        return room


# Process-wide singleton used by the API layer. `on_evict` is wired up in
# app/main.py, which owns the upload directory.
store = GameStore()
