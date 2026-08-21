"""API tests using FastAPI's TestClient.

TestClient runs the whole app in-process (no real server, no port, no
emulator) — you still just run `pytest`. It also supports WebSocket testing
via `websocket_connect`.

Each test gets a fresh store so rooms don't leak between tests (see the
autouse fixture below).
"""

import io

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import store


@pytest.fixture(autouse=True)
def clean_store():
    """Reset the in-memory store before every test."""
    store._rooms.clear()
    yield
    store._rooms.clear()


@pytest.fixture
def client():
    return TestClient(app)


def _join(client, code, name):
    resp = client.post(f"/rooms/{code}/join", json={"name": name})
    assert resp.status_code == 200
    return resp.json()["player_id"]


def _upload_photo(client, code, player_id, content=b"\xff\xd8\xff_fake_jpeg"):
    files = {"file": ("photo.jpg", io.BytesIO(content), "image/jpeg")}
    return client.post(
        f"/rooms/{code}/photos",
        params={"owner_id": player_id},
        files=files,
    )


# --- rooms + joining -----------------------------------------------------

def test_create_room_returns_code(client):
    resp = client.post("/rooms")
    assert resp.status_code == 200
    code = resp.json()["code"]
    assert len(code) == 5


def test_join_room(client):
    code = client.post("/rooms").json()["code"]
    resp = client.post(f"/rooms/{code}/join", json={"name": "Emma"})
    assert resp.status_code == 200
    body = resp.json()
    assert "player_id" in body
    assert body["is_host"] is True


def test_join_unknown_room_404(client):
    resp = client.post("/rooms/ZZZZZ/join", json={"name": "Emma"})
    assert resp.status_code == 404


def test_duplicate_name_returns_400(client):
    code = client.post("/rooms").json()["code"]
    _join(client, code, "Emma")
    resp = client.post(f"/rooms/{code}/join", json={"name": "Emma"})
    assert resp.status_code == 400


# --- photo upload --------------------------------------------------------

def test_photo_upload_accepts_image(client):
    code = client.post("/rooms").json()["code"]
    pid = _join(client, code, "Emma")
    resp = _upload_photo(client, code, pid)
    assert resp.status_code == 200
    assert "photo_id" in resp.json()
    assert resp.json()["url"]


def test_photo_upload_rejects_non_image(client):
    code = client.post("/rooms").json()["code"]
    pid = _join(client, code, "Emma")
    files = {"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")}
    resp = client.post(
        f"/rooms/{code}/photos", params={"owner_id": pid}, files=files
    )
    assert resp.status_code == 400


# --- state snapshot ------------------------------------------------------

def test_get_room_snapshot(client):
    code = client.post("/rooms").json()["code"]
    _join(client, code, "Emma")
    _join(client, code, "Jake")
    resp = client.get(f"/rooms/{code}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["state"] == "lobby"
    assert body["round_seconds"] == 10  # Room default before a game starts.
    assert {p["name"] for p in body["players"]} == {"Emma", "Jake"}


# --- websocket broadcast -------------------------------------------------

def test_websocket_receives_player_joined_event(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")

    # Host connects first, then a second player joins via REST -> host should
    # receive a broadcast event over the WebSocket.
    with client.websocket_connect(f"/ws/{code}/{host_id}") as ws:
        _join(client, code, "Jake")
        event = ws.receive_json()
        assert event["type"] == "player_joined"
        assert event["player"]["name"] == "Jake"


def test_start_game_drives_full_round_sequence(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    _upload_photo(client, code, host_id)

    with client.websocket_connect(f"/ws/{code}/{host_id}") as ws:
        # round_seconds=0 so the backend timer runs instantly in the test.
        resp = client.post(
            f"/rooms/{code}/start",
            json={"host_id": host_id, "total_rounds": 2, "round_seconds": 0},
        )
        assert resp.status_code == 200

        # The backend-driven timer broadcasts the whole game flow.
        events = [ws.receive_json() for _ in range(5)]
        assert [e["type"] for e in events] == [
            "round_started",
            "round_revealed",
            "round_started",
            "round_revealed",
            "game_finished",
        ]
        assert isinstance(events[0]["round_ends_at"], int)


def test_only_host_can_start(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    _upload_photo(client, code, host_id)
    resp = client.post(
        f"/rooms/{code}/start",
        json={"host_id": jake_id, "total_rounds": 1, "round_seconds": 0},
    )
    assert resp.status_code == 403


# --- resetting -------------------------------------------------------------

def test_host_can_reset_finished_room(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    _upload_photo(client, code, host_id)
    # A long round window so the guess below lands before the driver
    # auto-advances (round_seconds=0 would finish the round instantly).
    client.post(
        f"/rooms/{code}/start",
        json={"host_id": host_id, "total_rounds": 1, "round_seconds": 30},
    )
    # Jake correctly guesses Emma's photo -> scores a running total.
    guess_resp = client.post(
        f"/rooms/{code}/guess",
        json={"guesser_id": jake_id, "guessed_owner_id": host_id, "seconds_left": 8},
    )
    assert guess_resp.status_code == 200
    assert guess_resp.json()["points"] == 800

    # Finish the round manually rather than waiting out the timer.
    advance_resp = client.post(f"/rooms/{code}/advance")
    assert advance_resp.json()["state"] == "finished"

    resp = client.post(f"/rooms/{code}/reset", json={"host_id": host_id})
    assert resp.status_code == 200
    body = resp.json()
    assert body["state"] == "lobby"
    assert body["total_rounds"] == 0
    # Same room code, same players, scores carried over -- no rejoin needed.
    assert body["code"] == code
    assert {p["name"] for p in body["players"]} == {"Emma", "Jake"}
    jake = next(p for p in body["players"] if p["id"] == jake_id)
    assert jake["score"] == 800


def test_only_host_can_reset(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    resp = client.post(f"/rooms/{code}/reset", json={"host_id": jake_id})
    assert resp.status_code == 403


def test_reset_unknown_room_404(client):
    resp = client.post("/rooms/ZZZZZ/reset", json={"host_id": "whoever"})
    assert resp.status_code == 404


def test_cannot_reset_room_mid_round(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    _join(client, code, "Jake")
    _upload_photo(client, code, host_id)
    client.post(
        f"/rooms/{code}/start",
        json={"host_id": host_id, "total_rounds": 2, "round_seconds": 30},
    )

    resp = client.post(f"/rooms/{code}/reset", json={"host_id": host_id})
    assert resp.status_code == 400


def test_reset_broadcasts_room_reset_event(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    _join(client, code, "Jake")
    _upload_photo(client, code, host_id)
    client.post(
        f"/rooms/{code}/start",
        json={"host_id": host_id, "total_rounds": 1, "round_seconds": 0},
    )

    with client.websocket_connect(f"/ws/{code}/{host_id}") as ws:
        client.post(f"/rooms/{code}/reset", json={"host_id": host_id})
        event = ws.receive_json()
        assert event["type"] == "room_reset"
        assert {p["name"] for p in event["players"]} == {"Emma", "Jake"}
