"""In-memory store of active game rooms.

A single `GameStore` instance holds every room in a dict. State lives only in
RAM: it is lost on server restart, which is acceptable for short-lived party
games. Because it is in-memory, the backend must run as a SINGLE instance
(no horizontal scaling) — replicas would not share this dict.
"""

from __future__ import annotations

import random
from typing import Dict

from app.models import Room

# Ambiguous characters (0/O, 1/I) left out so codes are easy to read aloud.
_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
_CODE_LENGTH = 5


class RoomNotFound(Exception):
    """Raised when a room code does not exist."""


class GameStore:
    def __init__(self) -> None:
        self._rooms: Dict[str, Room] = {}

    def _generate_code(self) -> str:
        while True:
            code = "".join(random.choices(_CODE_ALPHABET, k=_CODE_LENGTH))
            if code not in self._rooms:
                return code

    def create_room(self) -> Room:
        code = self._generate_code()
        room = Room(code=code)
        self._rooms[code] = room
        return room

    def get_room(self, code: str) -> Room:
        code = code.upper()
        if code not in self._rooms:
            raise RoomNotFound(code)
        return self._rooms[code]


# Process-wide singleton used by the API layer.
store = GameStore()
