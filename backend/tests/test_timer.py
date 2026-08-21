"""Tests for the backend round timer (app/timer.py).

The RoundDriver runs a game's rounds over time. To keep tests instant, the
driver takes an injectable async `sleep` — tests pass a no-op so no real
waiting happens. We assert the *sequence* of events it emits and that the room
state machine advances correctly.

Run async tests via anyio's pytest plugin (installed with FastAPI). The
`anyio_backend` fixture pins it to asyncio.

The early-end tests below use the *real* asyncio.sleep (not the no-op) since
they need genuine wall-clock separation to prove the driver returns before
its timeout — each is wrapped in asyncio.wait_for with a short bound so a
regression fails fast instead of hanging the suite.
"""

import asyncio

import pytest

from app.game import Room, add_player, add_photo, start_game
from app.timer import RoundDriver


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

@pytest.mark.anyio
async def test_signal_early_end_returns_before_the_timeout():
    room = make_started_room(total_rounds=1, round_seconds=30)
    events = []
    driver = RoundDriver(room, on_event=lambda e: events.append(e["type"]))

    async def guess_soon():
        await asyncio.sleep(0.05)
        driver.signal_early_end(room.current_round)

    asyncio.ensure_future(guess_soon())
    await asyncio.wait_for(driver.run(), timeout=2)

    assert events == ["round_started", "round_revealed", "game_finished"]


@pytest.mark.anyio
async def test_signal_early_end_with_stale_round_index_is_a_noop():
    room = make_started_room(total_rounds=1, round_seconds=0)
    driver = RoundDriver(room, on_event=lambda e: None)
    # Signal for a round that isn't (yet) current -- ignored, the round still
    # ends via the normal (instant, since round_seconds=0) timeout path.
    driver.signal_early_end(round_index=99)
    await asyncio.wait_for(driver.run(), timeout=2)
    assert room.state.value == "finished"
