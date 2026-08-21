"""In-memory data models for the game.

Plain dataclasses — no database, no ORM. These shapes intentionally mirror the
Flutter models (Player, MockPhoto) so the future API contract lines up.
Written for Python 3.9 (uses typing.Optional/List, not `X | None`).
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class RoomState(str, enum.Enum):
    """Lifecycle of a game room."""

    LOBBY = "lobby"          # players joining, uploading photos
    IN_ROUND = "in_round"    # a photo is shown, guesses accepted
    REVEALING = "revealing"  # round over, showing the answer
    FINISHED = "finished"    # all rounds done, results ready


@dataclass
class Player:
    id: str
    name: str
    score: int = 0
    is_host: bool = False


@dataclass
class Photo:
    id: str
    owner_id: str  # the Player.id whose photo this is
    url: str       # path/URL to the stored image on disk


@dataclass
class Round:
    index: int
    photo: Photo
    # guesses maps player_id -> guessed_owner_id, so a player can't guess twice.
    guesses: Dict[str, str] = field(default_factory=dict)


@dataclass
class Room:
    code: str
    players: List[Player] = field(default_factory=list)
    photos: List[Photo] = field(default_factory=list)
    rounds: List[Round] = field(default_factory=list)
    current_round: int = 0
    state: RoomState = RoomState.LOBBY
    round_seconds: int = 10

    def player_by_id(self, player_id: str) -> Optional[Player]:
        for p in self.players:
            if p.id == player_id:
                return p
        return None

    def player_by_name(self, name: str) -> Optional[Player]:
        for p in self.players:
            if p.name == name:
                return p
        return None
