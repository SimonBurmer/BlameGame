"""Tests for the backend round timer (app/timer.py).

The RoundDriver runs a game's rounds over time. To keep tests instant, the
driver takes an injectable async `sleep` — tests pass a no-op so no real
waiting happens. We assert the *sequence* of events it emits and that the room
state machine advances correctly.

Run async tests via anyio's pytest plugin (installed with FastAPI). The
`anyio_backend` fixture pins it to asyncio.
"""

import pytest

from app.game import Room, add_player, add_photo, start_game
from app.models import RoomState
from app.timer import REVEAL_SECONDS, RoundDriver


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def _noop_sleep(_seconds: float) -> None:
    return None


def make_started_room(total_rounds: int, round_seconds: int = 0) -> Room:
    room = Room(code="TIMER")
    emma = add_player(room, "Emma")
    jake = add_player(room, "Jake")
    add_photo(room, owner_id=emma.id, url="/uploads/emma.jpg")
    add_photo(room, owner_id=jake.id, url="/uploads/jake.jpg")
    start_game(room, total_rounds=total_rounds, round_seconds=round_seconds)
    return room


@pytest.mark.anyio
async def test_driver_emits_round_and_finish_events_in_order():
    room = make_started_room(total_rounds=2)
    events = []

    driver = RoundDriver(
        room,
        sleep=_noop_sleep,
        on_event=lambda evt: events.append(evt["type"]),
    )
    await driver.run()

    # 2 rounds: start, reveal, start, reveal, then finish.
    assert events == [
        "round_started",
        "round_revealed",
        "round_started",
        "round_revealed",
        "game_finished",
    ]


@pytest.mark.anyio
async def test_driver_finishes_the_room_state():
    room = make_started_room(total_rounds=1)
    driver = RoundDriver(room, sleep=_noop_sleep, on_event=lambda e: None)
    await driver.run()
    assert room.state.value == "finished"


@pytest.mark.anyio
async def test_round_started_event_carries_photo_and_index():
    room = make_started_room(total_rounds=1)
    starts = []
    driver = RoundDriver(
        room,
        sleep=_noop_sleep,
        on_event=lambda e: starts.append(e) if e["type"] == "round_started" else None,
    )
    await driver.run()
    assert starts[0]["round_index"] == 0
    assert "photo" in starts[0]
    assert starts[0]["photo"]["owner_id"]


@pytest.mark.anyio
async def test_reveal_event_includes_correct_owner():
    room = make_started_room(total_rounds=1)
    reveals = []
    driver = RoundDriver(
        room,
        sleep=_noop_sleep,
        on_event=lambda e: reveals.append(e) if e["type"] == "round_revealed" else None,
    )
    await driver.run()
    assert "owner_id" in reveals[0]


@pytest.mark.anyio
async def test_round_started_event_carries_server_authoritative_deadline():
    room = make_started_room(total_rounds=1, round_seconds=10)
    starts = []
    driver = RoundDriver(
        room,
        sleep=_noop_sleep,
        time_fn=lambda: 1000.0,
        on_event=lambda e: starts.append(e) if e["type"] == "round_started" else None,
    )
    await driver.run()
    assert starts[0]["round_ends_at"] == int((1000.0 + 10) * 1000)


# --- early end -------------------------------------------------------------

def _guess(room, guesser, guessed_owner_id: str) -> None:
    room.rounds[room.current_round].guesses[guesser.id] = guessed_owner_id


@pytest.mark.anyio
async def test_round_ends_early_once_every_player_has_guessed():
    room = make_started_room(total_rounds=1, round_seconds=30)
    events = []
    steps = []

    async def counting_sleep(seconds: float) -> None:
        steps.append(seconds)

    for player in room.players:
        _guess(room, player, room.players[0].id)

    driver = RoundDriver(
        room,
        sleep=counting_sleep,
        on_event=lambda e: events.append(e["type"]),
    )
    await driver.run()

    assert events == ["round_started", "round_revealed", "game_finished"]
    # One poll to notice everyone guessed, then the reveal hold -- not the
    # full 30s round.
    assert steps == [0.2, REVEAL_SECONDS]


@pytest.mark.anyio
async def test_round_waits_out_the_timeout_when_only_some_have_guessed():
    room = make_started_room(total_rounds=1, round_seconds=30)
    steps = []

    async def counting_sleep(seconds: float) -> None:
        steps.append(seconds)

    _guess(room, room.players[0], room.players[0].id)

    driver = RoundDriver(room, sleep=counting_sleep, on_event=lambda e: None)
    await driver.run()

    # One player short -> no early end, the full 30s is polled out (plus the
    # reveal hold at the end of the round).
    assert sum(steps) == pytest.approx(30 + REVEAL_SECONDS)
    assert room.state.value == "finished"


@pytest.mark.anyio
async def test_reveal_is_held_before_the_next_round_starts():
    # Without the hold, round_revealed and the next round_started land in the
    # same tick and players never see whose photo it was.
    room = make_started_room(total_rounds=2, round_seconds=10)
    timeline = []

    async def recording_sleep(seconds: float) -> None:
        timeline.append(("sleep", seconds))

    driver = RoundDriver(
        room,
        sleep=recording_sleep,
        on_event=lambda e: timeline.append(("event", e["type"])),
    )
    await driver.run()

    # Between each reveal and the following round_started there must be a sleep.
    types = [t for t in timeline if t[0] == "event" or t[1] == REVEAL_SECONDS]
    reveal = types.index(("event", "round_revealed"))
    assert types[reveal + 1] == ("sleep", REVEAL_SECONDS)
    assert types[reveal + 2] == ("event", "round_started")


@pytest.mark.anyio
async def test_round_two_does_not_end_early_from_round_ones_guesses():
    # everyone_has_guessed reads the *current* round; if it ever looked at a
    # stale round, every round after the first would end instantly.
    room = make_started_room(total_rounds=2, round_seconds=30)
    steps = []

    async def counting_sleep(seconds: float) -> None:
        steps.append(seconds)

    for player in room.players:
        _guess(room, player, room.players[0].id)

    driver = RoundDriver(room, sleep=counting_sleep, on_event=lambda e: None)
    await driver.run()

    # Round 0 ends on the first poll; round 1 has no guesses and polls out.
    round_polls = [s for s in steps if s != REVEAL_SECONDS]
    assert sum(round_polls) == pytest.approx(0.2 + 30)


@pytest.mark.anyio
async def test_driver_stops_if_the_room_moved_on_while_it_waited():
    room = make_started_room(total_rounds=2, round_seconds=10)
    events = []

    async def hijacking_sleep(seconds: float) -> None:
        # Simulate the room being reset out from under the driver mid-round.
        room.state = RoomState.LOBBY

    driver = RoundDriver(
        room,
        sleep=hijacking_sleep,
        on_event=lambda e: events.append(e["type"]),
    )
    await driver.run()

    # It must not reveal a round it is no longer timing.
    assert events == ["round_started"]
