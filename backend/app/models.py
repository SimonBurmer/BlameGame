"""In-memory data models for the game.

Plain dataclasses — no database, no ORM. These shapes intentionally mirror the
Flutter models (Player, MockPhoto) so the future API contract lines up.
Written for Python 3.9 (uses typing.Optional/List, not `X | None`).
"""

from __future__ import annotations

import enum
import time
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
    # Epoch seconds when this round closes, set by the RoundDriver when the
    # round starts. The server scores from this rather than trusting a
    # client-supplied countdown, so a wrong phone clock or a patched client
    # can't mint points.
    ends_at: Optional[float] = None


@dataclass
class Room:
    code: str
    players: List[Player] = field(default_factory=list)
    photos: List[Photo] = field(default_factory=list)
    rounds: List[Round] = field(default_factory=list)
    current_round: int = 0
    state: RoomState = RoomState.LOBBY
    round_seconds: int = 10
    # Hardcore mode: photos are sampled and uploaded blind, with no preview or
    # reshuffle. Set once at room creation and never mutated — photos are
    # uploaded in the lobby before the game starts, so a flag carried on the
    # start call would arrive after they are already on disk, and a mutable
    # setting would let a host flip to hardcore after players had already
    # preview-approved what they shared.
    hardcore: bool = False
    # Bumped every time a game is started or reset. A RoundDriver captures it
    # at startup and re-checks after each await: the room is mutable shared
    # state, and an await is the only point another coroutine can change it.
    # Comparing the epoch tells a driver its game is over and it must stop,
    # which a state/round check alone can't (a reset-then-restart looks
    # identical to the round it was already driving).
    epoch: int = 0
    # Epoch seconds of the last time anyone touched this room. The store bumps
    # it on every lookup and evicts rooms that go quiet, so abandoned rooms and
    # their photos don't accumulate for the lifetime of the process.
    last_active: float = field(default_factory=time.time)

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
