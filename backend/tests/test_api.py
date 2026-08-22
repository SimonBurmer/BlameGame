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


# --- leaving / kicking -----------------------------------------------------

def test_player_can_leave_a_room(client):
    code = client.post("/rooms").json()["code"]
    _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")

    resp = client.post(f"/rooms/{code}/leave", json={"player_id": jake_id})

    assert resp.status_code == 200
    assert {p["name"] for p in resp.json()["players"]} == {"Emma"}


def test_leaving_broadcasts_player_left(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")

    with client.websocket_connect(f"/ws/{code}/{host_id}") as ws:
        resp = client.post(f"/rooms/{code}/leave", json={"player_id": jake_id})
        assert resp.status_code == 200
        event = ws.receive_json()

    assert event["type"] == "player_left"
    assert event["player_id"] == jake_id
    assert event["kicked"] is False
    assert {p["name"] for p in event["players"]} == {"Emma"}


def test_leaving_an_unknown_player_is_a_400(client):
    code = client.post("/rooms").json()["code"]
    _join(client, code, "Emma")
    resp = client.post(f"/rooms/{code}/leave", json={"player_id": "nobody"})
    assert resp.status_code == 400


def test_leave_unknown_room_404(client):
    resp = client.post("/rooms/ZZZZZ/leave", json={"player_id": "whoever"})
    assert resp.status_code == 404


def test_host_can_kick_a_player(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")

    resp = client.post(
        f"/rooms/{code}/kick", json={"host_id": host_id, "player_id": jake_id}
    )

    assert resp.status_code == 200
    assert {p["name"] for p in resp.json()["players"]} == {"Emma"}


def test_kick_broadcasts_player_left_flagged_as_kicked(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")

    with client.websocket_connect(f"/ws/{code}/{host_id}") as ws:
        resp = client.post(
            f"/rooms/{code}/kick", json={"host_id": host_id, "player_id": jake_id}
        )
        assert resp.status_code == 200
        event = ws.receive_json()

    # The flag is what lets the kicked player's client explain why it ejected.
    assert event["type"] == "player_left"
    assert event["kicked"] is True


def test_non_host_cannot_kick(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")

    resp = client.post(
        f"/rooms/{code}/kick", json={"host_id": jake_id, "player_id": host_id}
    )

    assert resp.status_code == 403
    # And the target is still in the room.
    assert {p["name"] for p in client.get(f"/rooms/{code}").json()["players"]} == {
        "Emma",
        "Jake",
    }


def test_host_cannot_kick_themselves(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    _join(client, code, "Jake")

    resp = client.post(
        f"/rooms/{code}/kick", json={"host_id": host_id, "player_id": host_id}
    )

    assert resp.status_code == 400


def test_kicking_an_unknown_player_is_a_400(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    resp = client.post(
        f"/rooms/{code}/kick", json={"host_id": host_id, "player_id": "nobody"}
    )
    assert resp.status_code == 400


def test_kick_unknown_room_404(client):
    resp = client.post(
        "/rooms/ZZZZZ/kick", json={"host_id": "whoever", "player_id": "someone"}
    )
    assert resp.status_code == 404


def test_host_leaving_hands_the_role_to_someone_else(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    _join(client, code, "Jake")

    resp = client.post(f"/rooms/{code}/leave", json={"player_id": host_id})

    assert resp.status_code == 200
    # A room with no host could never be started or reset again.
    players = resp.json()["players"]
    assert [p["name"] for p in players if p["is_host"]] == ["Jake"]


def test_new_host_can_actually_start_the_game(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    sam_id = _join(client, code, "Sam")
    _upload_photo(client, code, jake_id)
    _upload_photo(client, code, sam_id)

    client.post(f"/rooms/{code}/leave", json={"player_id": host_id})

    # The handover has to be real, not just a flag in the payload.
    resp = _start(client, code, jake_id)
    assert resp.status_code == 200


def test_leaving_removes_the_players_photos(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    _upload_photo(client, code, host_id)
    _upload_photo(client, code, jake_id)

    client.post(f"/rooms/{code}/leave", json={"player_id": jake_id})

    room = store.get_room(code)
    assert [p.owner_id for p in room.photos] == [host_id]


def test_kicked_player_is_refused_a_new_socket(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    client.post(f"/rooms/{code}/kick", json={"host_id": host_id, "player_id": jake_id})

    # The feed carries every photo URL in the game, so a removed player must
    # not be able to reconnect to it.
    with pytest.raises(Exception):
        with client.websocket_connect(f"/ws/{code}/{jake_id}"):
            pass


def test_leaving_mid_game_does_not_leave_a_round_on_a_departed_player(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    sam_id = _join(client, code, "Sam")
    _upload_photo(client, code, host_id)
    _upload_photo(client, code, jake_id)
    _upload_photo(client, code, sam_id)
    _start(client, code, host_id, total_rounds=4, round_seconds=30)

    client.post(f"/rooms/{code}/leave", json={"player_id": jake_id})

    room = store.get_room(code)
    # Any round still to be played must show a photo someone can be blamed for.
    for rnd in room.rounds[room.current_round:]:
        assert room.player_by_id(rnd.photo.owner_id) is not None


# --- serving photos --------------------------------------------------------

def test_uploaded_photo_can_be_fetched_back(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    url = _upload_photo(client, code, host_id).json()["url"]

    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.content == b"\xff\xd8\xff_fake_jpeg"


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
    assert list(tmp_path.rglob("*.jpg")) == []


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
