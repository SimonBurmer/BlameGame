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
