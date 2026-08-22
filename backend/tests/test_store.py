"""Unit tests for the in-memory GameStore (app/store.py)."""

import pytest

from app.store import GameStore, RoomNotFound


def test_create_room_returns_five_char_code():
    store = GameStore()
    room = store.create_room()
    assert len(room.code) == 5
    assert room.code.isalnum()
    assert room.code.isupper()


def test_created_room_is_retrievable():
    store = GameStore()
    room = store.create_room()
    assert store.get_room(room.code) is room


def test_get_unknown_room_raises():
    store = GameStore()
    with pytest.raises(RoomNotFound):
        store.get_room("ZZZZZ")


def test_room_codes_do_not_collide():
    store = GameStore()
    codes = {store.create_room().code for _ in range(200)}
    assert len(codes) == 200


class FakeClock:
    """Injectable clock, so eviction tests don't have to wait out a TTL."""

    def __init__(self, now=1000.0):
        self.now = now

    def __call__(self):
        return self.now


def test_idle_room_is_evicted_after_ttl():
    clock = FakeClock()
    store = GameStore(ttl_seconds=60, time_fn=clock)
    room = store.create_room()

    clock.now += 61
    with pytest.raises(RoomNotFound):
        store.get_room(room.code)


def test_room_is_kept_while_it_is_being_used():
    clock = FakeClock()
    store = GameStore(ttl_seconds=60, time_fn=clock)
    room = store.create_room()

    # Touched every 30s: never idle for a full TTL, so it must survive.
    for _ in range(10):
        clock.now += 30
        assert store.get_room(room.code) is room


def test_eviction_calls_on_evict_with_the_room_code():
    clock = FakeClock()
    evicted = []
    store = GameStore(ttl_seconds=60, time_fn=clock, on_evict=evicted.append)
    room = store.create_room()

    clock.now += 61
    assert store.sweep() == [room.code]
    assert evicted == [room.code]


def test_sweep_leaves_fresh_rooms_alone():
    clock = FakeClock()
    evicted = []
    store = GameStore(ttl_seconds=60, time_fn=clock, on_evict=evicted.append)
    stale = store.create_room()
    fresh = store.create_room()

    clock.now += 61
    # Keep only `fresh` alive; create_room sweeps too, so check what it dropped.
    fresh.last_active = clock.now
    assert store.sweep() == [stale.code]
    assert evicted == [stale.code]
    assert store.get_room(fresh.code) is fresh


def test_delete_room_removes_it_and_fires_on_evict():
    evicted = []
    store = GameStore(on_evict=evicted.append)
    room = store.create_room()

    store.delete_room(room.code)
    assert evicted == [room.code]
    with pytest.raises(RoomNotFound):
        store.get_room(room.code)


def test_delete_unknown_room_raises():
    store = GameStore()
    with pytest.raises(RoomNotFound):
        store.delete_room("ZZZZZ")
