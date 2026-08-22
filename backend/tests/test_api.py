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
from app.models import RoomState
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


def _start(client, code, host_id, **kwargs):
    """Start a game, defaulting to the shape most tests want."""
    body = {"host_id": host_id, "total_rounds": 1, "round_seconds": 1}
    body.update(kwargs)
    return client.post(f"/rooms/{code}/start", json=body)


def _finish(code):
    """Drive the room straight to FINISHED, bypassing the timer."""
    room = store.get_room(code)
    room.state = RoomState.FINISHED


def _current_owner(code):
    """Owner of the photo in the current round.

    start_game shuffles the pool, so tests that need a *correct* guess have to
    ask rather than assume.
    """
    room = store.get_room(code)
    return room.rounds[room.current_round].photo.owner_id


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


def test_start_puts_the_room_in_round_and_broadcasts_the_first_round(client):
    # The *timed* flow (reveal hold, early end, advance, finish) is driven by
    # RoundDriver and covered in test_timer.py with an injected sleep.
    # TestClient starves a background task the moment it really awaits, so
    # this asserts only what /start guarantees synchronously.
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    _upload_photo(client, code, host_id)
    _upload_photo(client, code, jake_id)

    resp = _start(client, code, host_id, total_rounds=2)
    assert resp.status_code == 200
    body = resp.json()
    assert body["state"] == "in_round"
    assert body["total_rounds"] == 2
    assert body["current_round"] == 0


def test_only_host_can_start(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    _upload_photo(client, code, host_id)
    _upload_photo(client, code, jake_id)
    resp = client.post(
        f"/rooms/{code}/start",
        json={"host_id": jake_id, "total_rounds": 1, "round_seconds": 1},
    )
    assert resp.status_code == 403


# --- early round end -------------------------------------------------------
#
# Round timing is driven by a background task that TestClient doesn't keep
# alive across separate synchronous requests, so the early-vs-timeout
# behaviour is asserted in test_timer.py. This only pins the request-level
# contract: a guess that completes the round still returns 200.

def test_guess_that_completes_the_round_does_not_error(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    _upload_photo(client, code, host_id)
    _upload_photo(client, code, jake_id)
    # A real, non-zero window so the round is still IN_ROUND when the
    # guesses below land (round_seconds=0 finishes the round immediately).
    client.post(
        f"/rooms/{code}/start",
        json={"host_id": host_id, "total_rounds": 1, "round_seconds": 30},
    )

    r1 = client.post(
        f"/rooms/{code}/guess",
        json={"guesser_id": host_id, "guessed_owner_id": host_id, "seconds_left": 25},
    )
    r2 = client.post(
        f"/rooms/{code}/guess",
        json={"guesser_id": jake_id, "guessed_owner_id": host_id, "seconds_left": 25},
    )
    assert r1.status_code == 200
    assert r2.status_code == 200


# --- resetting -------------------------------------------------------------

def test_host_can_reset_finished_room(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    _upload_photo(client, code, host_id)
    _upload_photo(client, code, jake_id)
    # A long round window so the guess below lands before the driver
    # auto-advances (round_seconds=0 would finish the round instantly).
    client.post(
        f"/rooms/{code}/start",
        json={"host_id": host_id, "total_rounds": 1, "round_seconds": 30},
    )
    # A correct guess -> scores a running total.
    owner = _current_owner(code)
    guesser = jake_id if owner == host_id else host_id
    guess_resp = client.post(
        f"/rooms/{code}/guess",
        json={"guesser_id": guesser, "guessed_owner_id": owner},
    )
    assert guess_resp.status_code == 200
    # No RoundDriver runs under TestClient, so no deadline was recorded and
    # the guess scores the full round length (30s * 100).
    assert guess_resp.json()["points"] == 3000

    # Finish the game outright rather than waiting out the timer.
    _finish(code)

    resp = client.post(f"/rooms/{code}/reset", json={"host_id": host_id})
    assert resp.status_code == 200
    body = resp.json()
    assert body["state"] == "lobby"
    assert body["total_rounds"] == 0
    # Same room code, same players, scores carried over -- no rejoin needed.
    assert body["code"] == code
    assert {p["name"] for p in body["players"]} == {"Emma", "Jake"}
    scorer = next(p for p in body["players"] if p["id"] == guesser)
    assert scorer["score"] == 3000


def test_only_host_can_reset(client):
    code = client.post("/rooms").json()["code"]
    _join(client, code, "Emma")  # host
    jake_id = _join(client, code, "Jake")
    resp = client.post(f"/rooms/{code}/reset", json={"host_id": jake_id})
    assert resp.status_code == 403


def test_reset_unknown_room_404(client):
    resp = client.post("/rooms/ZZZZZ/reset", json={"host_id": "whoever"})
    assert resp.status_code == 404


def test_cannot_reset_room_mid_round(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    _upload_photo(client, code, host_id)
    _upload_photo(client, code, jake_id)
    client.post(
        f"/rooms/{code}/start",
        json={"host_id": host_id, "total_rounds": 2, "round_seconds": 30},
    )

    resp = client.post(f"/rooms/{code}/reset", json={"host_id": host_id})
    assert resp.status_code == 400


def test_reset_broadcasts_room_reset_event(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    _upload_photo(client, code, host_id)
    _upload_photo(client, code, jake_id)
    _start(client, code, host_id, round_seconds=30)
    # Finish the game outright: reset is only allowed once it's over, and no
    # RoundDriver progresses under TestClient.
    _finish(code)

    with client.websocket_connect(f"/ws/{code}/{host_id}") as ws:
        resp = client.post(f"/rooms/{code}/reset", json={"host_id": host_id})
        assert resp.status_code == 200
        event = ws.receive_json()
        assert event["type"] == "room_reset"
        assert {p["name"] for p in event["players"]} == {"Emma", "Jake"}


# --- serving photos --------------------------------------------------------

def test_uploaded_photo_can_be_fetched_back(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    url = _upload_photo(client, code, host_id).json()["url"]

    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.content == b"\xff\xd8\xff_fake_jpeg"


def test_png_round_trips_as_png(client):
    # Uploads used to be stored as .jpg whatever the bytes were, so a PNG came
    # back labelled image/jpeg.
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    png = b"\x89PNG\r\n\x1a\n_fake_png"
    # Header deliberately lies: the bytes decide.
    url = _upload_photo(client, code, host_id, content=png).json()["url"]
    assert url.endswith(".png")

    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.content == png
    assert resp.headers["content-type"] == "image/png"


def test_jpeg_round_trips_as_jpeg(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    url = _upload_photo(client, code, host_id).json()["url"]
    assert url.endswith(".jpg")
    assert client.get(url).headers["content-type"] == "image/jpeg"


def test_photo_route_does_not_serve_files_outside_the_upload_dir(client):
    # `/rooms/../photos/<name>` used to resolve out of UPLOAD_DIR and serve
    # arbitrary files from the working directory.
    for code, filename in [
        ("..", "pyproject.toml"),
        ("%2e%2e", "pyproject.toml"),
        (".", "app"),
    ]:
        resp = client.get(f"/rooms/{code}/photos/{filename}")
        assert resp.status_code == 404, f"{code}/{filename} leaked: {resp.status_code}"


# --- upload limits ---------------------------------------------------------

def test_oversized_upload_is_rejected(client):
    from app.main import MAX_PHOTO_BYTES

    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    too_big = b"\xff\xd8\xff" + b"\x00" * MAX_PHOTO_BYTES
    resp = _upload_photo(client, code, host_id, content=too_big)
    assert resp.status_code == 413


def test_upload_rejects_bytes_that_are_not_an_image(client):
    # The content-type header is client-supplied; the bytes are what count.
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    resp = _upload_photo(client, code, host_id, content=b"<script>alert(1)</script>")
    assert resp.status_code == 400


def test_upload_is_capped_per_player(client):
    from app.game import MAX_PHOTOS_PER_PLAYER

    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    for _ in range(MAX_PHOTOS_PER_PLAYER):
        assert _upload_photo(client, code, host_id).status_code == 200
    assert _upload_photo(client, code, host_id).status_code == 400


def test_upload_rejected_once_the_game_has_started(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    _upload_photo(client, code, host_id)
    _upload_photo(client, code, jake_id)
    _start(client, code, host_id)

    # A late upload would never be used, so say so rather than accept it.
    assert _upload_photo(client, code, host_id).status_code == 400


def test_a_rejected_upload_leaves_no_file_behind(client, tmp_path, monkeypatch):
    import app.main as main

    monkeypatch.setattr(main, "UPLOAD_DIR", tmp_path)
    code = client.post("/rooms").json()["code"]
    _join(client, code, "Emma")

    resp = _upload_photo(client, code, "not-a-player")
    assert resp.status_code == 400
    assert [p for p in tmp_path.rglob("*") if p.is_file()] == []


def test_room_has_a_player_cap(client):
    from app.game import MAX_PLAYERS

    code = client.post("/rooms").json()["code"]
    for i in range(MAX_PLAYERS):
        assert client.post(f"/rooms/{code}/join", json={"name": f"P{i}"}).status_code == 200
    resp = client.post(f"/rooms/{code}/join", json={"name": "OneTooMany"})
    assert resp.status_code == 400


# --- guessing --------------------------------------------------------------

def test_guess_for_a_stale_round_is_rejected(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    _upload_photo(client, code, host_id)
    _upload_photo(client, code, jake_id)
    _start(client, code, host_id, total_rounds=2, round_seconds=30)

    # A guess still in flight when the round rolls over must not be recorded
    # against the round the player never saw.
    resp = client.post(
        f"/rooms/{code}/guess",
        json={
            "guesser_id": jake_id,
            "guessed_owner_id": host_id,
            "round_index": 1,  # server is still on round 0
        },
    )
    assert resp.status_code == 400
    assert "already ended" in resp.json()["detail"]


def test_seconds_left_is_derived_from_the_server_clock(client):
    # The client no longer supplies it, so a forged value cannot mint points.
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    _upload_photo(client, code, host_id)
    _upload_photo(client, code, jake_id)
    _start(client, code, host_id, round_seconds=10)

    owner = _current_owner(code)
    guesser = jake_id if owner == host_id else host_id
    resp = client.post(
        f"/rooms/{code}/guess",
        json={
            "guesser_id": guesser,
            "guessed_owner_id": owner,
            "seconds_left": 99999,  # ignored
        },
    )
    assert resp.status_code == 200
    assert resp.json()["points"] == 1000  # 10s round * 100, not 9,999,900


# --- websocket -------------------------------------------------------------

def test_websocket_accepts_a_lowercased_room_code(client):
    # Sockets used to register under the raw path code while broadcasts
    # targeted the canonical one, so a lowercase code silently got nothing.
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")

    with client.websocket_connect(f"/ws/{code.lower()}/{host_id}") as ws:
        _join(client, code, "Jake")
        event = ws.receive_json()
        assert event["type"] == "player_joined"


def test_websocket_rejects_a_non_player(client):
    code = client.post("/rooms").json()["code"]
    _join(client, code, "Emma")

    with pytest.raises(Exception):
        with client.websocket_connect(f"/ws/{code}/not-a-player") as ws:
            ws.receive_json()


# --- ending a room ---------------------------------------------------------

def test_host_can_end_a_room_and_its_photos_go_with_it(client, tmp_path, monkeypatch):
    import app.main as main

    monkeypatch.setattr(main, "UPLOAD_DIR", tmp_path)
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    _upload_photo(client, code, host_id)
    assert (tmp_path / code).is_dir()

    resp = client.request("DELETE", f"/rooms/{code}", params={"host_id": host_id})
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True
    assert not (tmp_path / code).exists()
    assert client.get(f"/rooms/{code}").status_code == 404


def test_only_host_can_end_a_room(client):
    code = client.post("/rooms").json()["code"]
    _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")

    resp = client.request("DELETE", f"/rooms/{code}", params={"host_id": jake_id})
    assert resp.status_code == 403
    assert client.get(f"/rooms/{code}").status_code == 200


def test_end_unknown_room_404(client):
    resp = client.request("DELETE", "/rooms/ZZZZZ", params={"host_id": "whoever"})
    assert resp.status_code == 404


def test_ending_a_room_broadcasts_room_closed(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")

    with client.websocket_connect(f"/ws/{code}/{host_id}") as ws:
        resp = client.request("DELETE", f"/rooms/{code}", params={"host_id": host_id})
        assert resp.status_code == 200
        assert ws.receive_json()["type"] == "room_closed"


def test_evicting_a_stale_room_deletes_its_uploads(client, tmp_path, monkeypatch):
    """The TTL sweep must take the photos with it, not just the dict entry."""
    import app.main as main

    monkeypatch.setattr(main, "UPLOAD_DIR", tmp_path)
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    _upload_photo(client, code, host_id)
    assert (tmp_path / code).is_dir()

    # Age the room past the TTL rather than waiting six hours for it.
    store.get_room(code).last_active -= store._ttl + 1
    assert store.sweep() == [code]
    assert not (tmp_path / code).exists()


def test_upload_cleanup_refuses_a_path_outside_the_upload_dir(tmp_path, monkeypatch):
    import app.main as main

    monkeypatch.setattr(main, "UPLOAD_DIR", tmp_path)
    victim = tmp_path.parent / "not-ours"
    victim.mkdir()

    main._delete_room_uploads("../not-ours")
    assert victim.is_dir()
