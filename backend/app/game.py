"""Room state machine and game rules.

Pure-ish logic operating on a `Room`: joining, starting, guessing, scoring,
advancing rounds, and ranking. No FastAPI, no WebSockets, no disk here — that
keeps every rule fast and easy to unit-test.
"""

from __future__ import annotations

import random
import uuid
from typing import List

from app.models import Photo, Player, Room, RoomState, Round
from app.scoring import points_for_guess

# Re-export Room so tests/importers can grab it from one place.
__all__ = [
    "Room",
    "GameError",
    "add_player",
    "add_photo",
    "start_game",
    "current_photo",
    "submit_guess",
    "advance_round",
    "rankings",
]


class GameError(Exception):
    """Raised when an action is not allowed in the current game state."""


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


def add_player(room: Room, name: str) -> Player:
    """Add a player to a room. First player becomes host. Names are unique."""
    if room.state != RoomState.LOBBY:
        raise GameError("cannot join a game that has already started")
    if room.player_by_name(name) is not None:
        raise GameError(f"name '{name}' is already taken in this room")
    player = Player(
        id=_new_id(),
        name=name,
        is_host=len(room.players) == 0,
    )
    room.players.append(player)
    return player


def add_photo(room: Room, *, owner_id: str, url: str) -> Photo:
    """Register an uploaded photo for a player."""
    if room.player_by_id(owner_id) is None:
        raise GameError("photo owner is not a player in this room")
    photo = Photo(id=_new_id(), owner_id=owner_id, url=url)
    room.photos.append(photo)
    return photo


def start_game(room: Room, *, total_rounds: int = 5) -> None:
    """Begin the game: validate, build the rounds, enter the first round."""
    if room.state != RoomState.LOBBY:
        raise GameError("game has already started")
    if len(room.players) < 2:
        raise GameError("need at least 2 players to start")
    if len(room.photos) < 1:
        raise GameError("need at least 1 photo to start")

    pool = list(room.photos)
    random.shuffle(pool)
    # Cycle through the shuffled photos if there are fewer photos than rounds.
    room.rounds = [
        Round(index=i, photo=pool[i % len(pool)]) for i in range(total_rounds)
    ]
    room.current_round = 0
    room.state = RoomState.IN_ROUND


def current_photo(room: Room) -> Photo:
    """The photo being shown in the current round."""
    if not room.rounds:
        raise GameError("game has not started")
    return room.rounds[room.current_round].photo


def submit_guess(
    room: Room,
    *,
    guesser_id: str,
    guessed_owner_id: str,
    seconds_left: int,
) -> int:
    """Record a guess, award points, and return the points earned."""
    if room.state != RoomState.IN_ROUND:
        raise GameError("guesses are only allowed during a round")

    guesser = room.player_by_id(guesser_id)
    if guesser is None:
        raise GameError("guesser is not a player in this room")

    this_round = room.rounds[room.current_round]
    if guesser_id in this_round.guesses:
        raise GameError("player has already guessed this round")
    this_round.guesses[guesser_id] = guessed_owner_id

    correct = guessed_owner_id == this_round.photo.owner_id
    points = points_for_guess(correct=correct, seconds_left=seconds_left)
    guesser.score += points
    return points


def advance_round(room: Room) -> None:
    """Move to the next round, or finish the game if this was the last one."""
    if room.state == RoomState.FINISHED:
        raise GameError("game is already finished")
    if room.current_round >= len(room.rounds) - 1:
        room.state = RoomState.FINISHED
    else:
        room.current_round += 1
        room.state = RoomState.IN_ROUND


def rankings(room: Room) -> List[Player]:
    """Players sorted by score, highest first (ties keep join order)."""
    return sorted(room.players, key=lambda p: p.score, reverse=True)
