"""Room state machine and game rules.

Pure-ish logic operating on a `Room`: joining, starting, guessing, scoring,
advancing rounds, and ranking. No FastAPI, no WebSockets, no disk here — that
keeps every rule fast and easy to unit-test.
"""

from __future__ import annotations

import math
import random
import time
import uuid
from typing import List, Optional

from app.models import Photo, Player, Room, RoomState, Round
from app.scoring import points_for_guess

# Re-export Room so tests/importers can grab it from one place.
__all__ = [
    "Room",
    "GameError",
    "add_player",
    "remove_player",
    "add_photo",
    "start_game",
    "current_photo",
    "submit_guess",
    "seconds_left_in_round",
    "everyone_has_guessed",
    "advance_round",
    "rankings",
    "reset_room",
]


# A party game, not a stadium: caps keep one client from filling the room,
# the photo pool, or the disk.
MAX_PLAYERS = 12
MAX_PHOTOS_PER_PLAYER = 10


class GameError(Exception):
    """Raised when an action is not allowed in the current game state."""


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


def add_player(room: Room, name: str) -> Player:
    """Add a player to a room. First player becomes host. Names are unique."""
    if room.state != RoomState.LOBBY:
        raise GameError("cannot join a game that has already started")
    if len(room.players) >= MAX_PLAYERS:
        raise GameError(f"room is full (max {MAX_PLAYERS} players)")
    if room.player_by_name(name) is not None:
        raise GameError(f"name '{name}' is already taken in this room")
    player = Player(
        id=_new_id(),
        name=name,
        is_host=len(room.players) == 0,
    )
    room.players.append(player)
    return player


def remove_player(room: Room, player_id: str) -> Player:
    """Remove a player from a room. Shared by leaving and being kicked.

    Their photos go with them -- a departed player can't be guessed, so any
    round still pointing at their photo would be unwinnable. Rounds already
    played keep their photo (the guesses are scored and the reveal happened);
    only rounds not yet reached are re-pointed at a surviving photo.

    The host leaving hands the role to the next player, so the room never ends
    up with no one able to start or reset it.
    """
    player = room.player_by_id(player_id)
    if player is None:
        raise GameError("player is not in this room")

    room.players.remove(player)
    room.photos = [p for p in room.photos if p.owner_id != player_id]

    if player.is_host and room.players:
        room.players[0].is_host = True

    # Their guesses in the current round no longer count towards "everyone has
    # guessed", and stale entries would keep the round from ever closing early.
    for rnd in room.rounds:
        rnd.guesses.pop(player_id, None)

    if room.state in (RoomState.IN_ROUND, RoomState.REVEALING):
        _repoint_pending_rounds(room)

    return player


def _repoint_pending_rounds(room: Room) -> None:
    """Point rounds not yet played at a photo whose owner is still here.

    With too few players or no photos left there is no game to finish, so the
    room jumps to FINISHED rather than running out the clock on rounds nobody
    can win. The RoundDriver sees the state change and stops.
    """
    if len(room.players) < 2 or not room.photos:
        room.state = RoomState.FINISHED
        return
    pool = list(room.photos)
    for i, rnd in enumerate(room.rounds[room.current_round :]):
        if room.player_by_id(rnd.photo.owner_id) is None:
            rnd.photo = pool[i % len(pool)]


def add_photo(room: Room, *, owner_id: str, url: str) -> Photo:
    """Register an uploaded photo for a player."""
    if room.player_by_id(owner_id) is None:
        raise GameError("photo owner is not a player in this room")
    if room.state != RoomState.LOBBY:
        raise GameError("photos can only be added before the game starts")
    owned = sum(1 for p in room.photos if p.owner_id == owner_id)
    if owned >= MAX_PHOTOS_PER_PLAYER:
        raise GameError(f"at most {MAX_PHOTOS_PER_PLAYER} photos per player")
    photo = Photo(id=_new_id(), owner_id=owner_id, url=url)
    room.photos.append(photo)
    return photo


def start_game(room: Room, *, total_rounds: int = 5, round_seconds: int = 10) -> None:
    """Begin the game: validate, build the rounds, enter the first round."""
    if room.state != RoomState.LOBBY:
        raise GameError("game has already started")
    if len(room.players) < 2:
        raise GameError("need at least 2 players to start")
    # Photos from at least two people, otherwise every round shows the same
    # player's pictures: they recognise all of them and win by default while
    # everyone else can only guess that one name.
    if len({p.owner_id for p in room.photos}) < 2:
        raise GameError("need photos from at least 2 players to start")
    pool = list(room.photos)
    random.shuffle(pool)
    # Cycle through the shuffled photos if there are fewer photos than rounds.
    room.rounds = [
        Round(index=i, photo=pool[i % len(pool)]) for i in range(total_rounds)
    ]
    room.current_round = 0
    room.round_seconds = round_seconds
    room.state = RoomState.IN_ROUND
    # New game, new epoch: any driver still sleeping on the previous one must
    # not wake up and drive this game too.
    room.epoch += 1


def current_photo(room: Room) -> Photo:
    """The photo being shown in the current round."""
    if not room.rounds:
        raise GameError("game has not started")
    return room.rounds[room.current_round].photo


def seconds_left_in_round(room: Room, rnd: Round, now: Optional[float] = None) -> int:
    """Seconds remaining in `rnd`, measured against the server's own clock.

    Falls back to the full round length when no deadline has been recorded
    (a round that was never driven by the RoundDriver, as in unit tests).
    """
    if rnd.ends_at is None:
        return room.round_seconds
    now = time.time() if now is None else now
    remaining = math.ceil(rnd.ends_at - now)
    return max(0, min(room.round_seconds, remaining))


def submit_guess(
    room: Room,
    *,
    guesser_id: str,
    guessed_owner_id: str,
    round_index: Optional[int] = None,
    now: Optional[float] = None,
) -> int:
    """Record a guess, award points, and return the points earned.

    `round_index` is the round the guesser believed they were answering. A
    guess still in flight when the round rolls over would otherwise be
    recorded against the next round -- scoring it against a photo the player
    never saw and consuming the guess slot they need for the new round.
    """
    if room.state != RoomState.IN_ROUND:
        raise GameError("guesses are only allowed during a round")

    guesser = room.player_by_id(guesser_id)
    if guesser is None:
        raise GameError("guesser is not a player in this room")

    if round_index is not None and round_index != room.current_round:
        raise GameError("that round has already ended")

    this_round = room.rounds[room.current_round]
    if guesser_id in this_round.guesses:
        raise GameError("player has already guessed this round")
    this_round.guesses[guesser_id] = guessed_owner_id

    correct = guessed_owner_id == this_round.photo.owner_id
    points = points_for_guess(
        correct=correct,
        seconds_left=seconds_left_in_round(room, this_round, now),
    )
    guesser.score += points
    return points


def everyone_has_guessed(room: Room) -> bool:
    """True once every player has guessed the current round."""
    if not room.rounds:
        return False
    return len(room.rounds[room.current_round].guesses) >= len(room.players)


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


def reset_room(room: Room) -> None:
    """Send a finished (or mid-lobby) room back to LOBBY for a new round.

    Same room code, same players and photos, same host — only rounds are
    cleared, so the group can play again without re-sharing the code or
    re-uploading photos. Scores are NOT reset: players who stay in the room
    keep a running total across every round played there.
    """
    if room.state == RoomState.IN_ROUND or room.state == RoomState.REVEALING:
        raise GameError("cannot reset a room while a round is in progress")
    room.rounds = []
    room.current_round = 0
    room.state = RoomState.LOBBY
    room.epoch += 1
