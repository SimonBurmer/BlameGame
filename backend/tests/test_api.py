"""API tests using FastAPI's TestClient.

TestClient runs the whole app in-process (no real server, no port, no
emulator) — you still just run `pytest`. It also supports WebSocket testing
via `websocket_connect`.

Each test gets a fresh store so rooms don't leak between tests (see the
autouse fixture below).
"""

import io

import pytest
from fastapi import WebSocketDisconnect
from fastapi.testclient import TestClient

from app.connection import manager
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


def test_create_room_defaults_to_normal_mode(client):
    # No body at all still works, and is not hardcore.
    assert client.post("/rooms").json()["hardcore"] is False
    code = client.post("/rooms", json={}).json()["code"]
    assert client.get(f"/rooms/{code}").json()["hardcore"] is False


def test_create_hardcore_room_reports_mode_in_snapshot(client):
    # Every client learns the mode from the snapshot, not from local state.
    code = client.post("/rooms", json={"hardcore": True}).json()["code"]
    _join(client, code, "Emma")
    assert client.get(f"/rooms/{code}").json()["hardcore"] is True


def test_hardcore_mode_is_not_mutable_after_creation(client):
    # Starting the game must not be able to flip the mode: photos are already
    # uploaded by then, so a late toggle would retroactively break the promise.
    code = client.post("/rooms", json={"hardcore": False}).json()["code"]
    host = _join(client, code, "Emma")
    _join(client, code, "Liam")
    client.post(f"/rooms/{code}/start", json={"host_id": host, "hardcore": True})
    assert client.get(f"/rooms/{code}").json()["hardcore"] is False


def test_host_sets_settings_from_the_lobby(client):
    code = client.post("/rooms").json()["code"]
    host = _join(client, code, "Emma")
    resp = client.post(
        f"/rooms/{code}/settings",
        json={"host_id": host, "total_rounds": 8, "round_seconds": 20, "hardcore": True},
    )
    assert resp.status_code == 200
    snapshot = client.get(f"/rooms/{code}").json()
    assert snapshot["total_rounds"] == 8
    assert snapshot["round_seconds"] == 20
    assert snapshot["hardcore"] is True


def test_start_uses_the_lobby_settings(client):
    code = client.post("/rooms").json()["code"]
    host = _join(client, code, "Emma")
    jake = _join(client, code, "Jake")
    client.post(
        f"/rooms/{code}/settings",
        json={"host_id": host, "total_rounds": 3, "round_seconds": 25},
    )
    _upload_photo(client, code, host)
    _upload_photo(client, code, jake)
    body = client.post(f"/rooms/{code}/start", json={"host_id": host}).json()
    assert body["total_rounds"] == 3
    assert body["round_seconds"] == 25


def test_only_the_host_can_change_settings(client):
    code = client.post("/rooms").json()["code"]
    _join(client, code, "Emma")
    jake = _join(client, code, "Jake")
    resp = client.post(
        f"/rooms/{code}/settings", json={"host_id": jake, "total_rounds": 9}
    )
    assert resp.status_code == 403
    assert client.get(f"/rooms/{code}").json()["total_rounds"] == 5


def test_hardcore_locks_server_side_once_a_photo_is_uploaded(client):
    # The adversarial case: a client can post whatever it likes, so the lock
    # lives on the server. Flipping the mode after someone has already
    # preview-approved and shared a photo must be refused.
    code = client.post("/rooms").json()["code"]
    host = _join(client, code, "Emma")
    _upload_photo(client, code, host)

    resp = client.post(f"/rooms/{code}/settings", json={"host_id": host, "hardcore": True})
    assert resp.status_code == 400
    assert "locked" in resp.json()["detail"]
    assert client.get(f"/rooms/{code}").json()["hardcore"] is False


def test_rounds_stay_editable_after_photos_are_uploaded(client):
    code = client.post("/rooms").json()["code"]
    host = _join(client, code, "Emma")
    _upload_photo(client, code, host)
    resp = client.post(
        f"/rooms/{code}/settings",
        json={"host_id": host, "total_rounds": 7, "round_seconds": 15},
    )
    assert resp.status_code == 200
    snapshot = client.get(f"/rooms/{code}").json()
    assert (snapshot["total_rounds"], snapshot["round_seconds"]) == (7, 15)


def test_restating_the_current_hardcore_value_is_allowed_after_photos(client):
    # Only a *change* is locked; a client resending the unchanged value (a
    # full-settings post) must not be rejected.
    code = client.post("/rooms").json()["code"]
    host = _join(client, code, "Emma")
    _upload_photo(client, code, host)
    resp = client.post(
        f"/rooms/{code}/settings", json={"host_id": host, "hardcore": False}
    )
    assert resp.status_code == 200


def test_settings_cannot_be_changed_once_the_game_is_running(client):
    code = client.post("/rooms").json()["code"]
    host = _join(client, code, "Emma")
    jake = _join(client, code, "Jake")
    _upload_photo(client, code, host)
    _upload_photo(client, code, jake)
    client.post(f"/rooms/{code}/start", json={"host_id": host})
    resp = client.post(
        f"/rooms/{code}/settings", json={"host_id": host, "total_rounds": 2}
    )
    assert resp.status_code == 400


def test_settings_are_broadcast_to_every_client(client):
    code = client.post("/rooms").json()["code"]
    host = _join(client, code, "Emma")
    jake = _join(client, code, "Jake")
    with client.websocket_connect(f"/ws/{code}/{jake}") as ws:
        client.post(
            f"/rooms/{code}/settings", json={"host_id": host, "total_rounds": 6}
        )
        event = ws.receive_json()
    assert event["type"] == "settings_updated"
    assert event["total_rounds"] == 6


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


def _start_two_player_round(client, seconds=30):
    """A room in IN_ROUND with two players who each contributed a photo."""
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    _upload_photo(client, code, host_id)
    _upload_photo(client, code, jake_id)
    _start(client, code, host_id, round_seconds=seconds)
    return code, host_id, jake_id


def _record_broadcasts(monkeypatch):
    """Capture what the app broadcasts, without a socket to read from.

    Asserting via a real socket means a *missing* broadcast blocks forever in
    receive_json() instead of failing, so the negative case is checked here.
    """
    sent = []
    original = manager.broadcast

    async def spy(room_code, message):
        sent.append(message)
        await original(room_code, message)

    monkeypatch.setattr(manager, "broadcast", spy)
    return sent


def test_guess_result_reaches_the_other_players(client, monkeypatch):
    """The scoreboard is driven by the broadcast, not by the guesser's response.

    Everyone else only learns a guess happened over the socket; if the guess
    endpoint returned its result without broadcasting, the guesser would see
    their points and every other client would show a frozen scoreboard.
    """
    code, host_id, jake_id = _start_two_player_round(client)
    sent = _record_broadcasts(monkeypatch)

    with client.websocket_connect(f"/ws/{code}/{host_id}") as host_ws:
        owner = _current_owner(code)
        guesser = jake_id if owner == host_id else host_id
        client.post(
            f"/rooms/{code}/guess",
            json={"guesser_id": guesser, "guessed_owner_id": owner},
        )

        results = [m for m in sent if m["type"] == "guess_result"]
        assert len(results) == 1, "the guess was not broadcast"

        # ...and it actually reaches another player's socket, not just the bus.
        event = host_ws.receive_json()
        assert event["type"] == "guess_result"
        assert event["guesser_id"] == guesser
        assert event["correct"] is True
        assert event["points"] > 0


def test_a_wrong_guess_scores_nothing_and_says_so(client, monkeypatch):
    # points > 0 is what marks a guess correct, in the response and the
    # broadcast alike, so a wrong guess must score exactly zero.
    code, host_id, jake_id = _start_two_player_round(client)
    sent = _record_broadcasts(monkeypatch)

    owner = _current_owner(code)
    guesser = jake_id if owner == host_id else host_id
    wrong = host_id if owner != host_id else jake_id

    resp = client.post(
        f"/rooms/{code}/guess",
        json={"guesser_id": guesser, "guessed_owner_id": wrong},
    )
    assert resp.status_code == 200
    assert resp.json() == {"points": 0, "correct": False}

    results = [m for m in sent if m["type"] == "guess_result"]
    assert len(results) == 1
    assert results[0]["correct"] is False
    assert results[0]["points"] == 0


def test_guessing_twice_in_a_round_is_rejected(client):
    # One guess per player per round; a second must not top up the score.
    code, host_id, jake_id = _start_two_player_round(client)
    owner = _current_owner(code)
    guesser = jake_id if owner == host_id else host_id

    first = client.post(
        f"/rooms/{code}/guess",
        json={"guesser_id": guesser, "guessed_owner_id": owner},
    )
    assert first.status_code == 200
    scored = client.get(f"/rooms/{code}").json()["players"]

    second = client.post(
        f"/rooms/{code}/guess",
        json={"guesser_id": guesser, "guessed_owner_id": owner},
    )
    assert second.status_code == 400
    assert client.get(f"/rooms/{code}").json()["players"] == scored


def test_guess_from_a_non_player_is_rejected(client):
    # guesser_id is client-supplied: an unknown id must not mint a score entry.
    code, host_id, _ = _start_two_player_round(client)
    resp = client.post(
        f"/rooms/{code}/guess",
        json={"guesser_id": "not-a-player", "guessed_owner_id": host_id},
    )
    assert resp.status_code == 400


def test_guess_in_an_unknown_room_is_404(client):
    resp = client.post(
        "/rooms/ZZZZZ/guess",
        json={"guesser_id": "a", "guessed_owner_id": "b"},
    )
    assert resp.status_code == 404


def test_guess_before_the_game_starts_is_rejected(client):
    # A lobby has no round to answer, so there is nothing to score against.
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")
    resp = client.post(
        f"/rooms/{code}/guess",
        json={"guesser_id": jake_id, "guessed_owner_id": host_id},
    )
    assert resp.status_code == 400


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
    # Back in the lobby the snapshot reports the configured round count (the
    # one the last game was started with), not the cleared round list.
    assert body["total_rounds"] == 1
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


def test_kick_closes_the_kicked_players_open_socket(client):
    """A client that ignores player_left must still stop receiving the feed.

    Asserted server-side (the socket is deregistered and a later broadcast is
    not delivered to it), not by a cooperating client hanging up.
    """
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")

    with client.websocket_connect(f"/ws/{code}/{host_id}") as host_ws:
        with client.websocket_connect(f"/ws/{code}/{jake_id}") as jake_ws:
            client.post(
                f"/rooms/{code}/kick", json={"host_id": host_id, "player_id": jake_id}
            )

            # Server-side: Jake holds no socket in this room any more.
            assert manager._players.get((code, jake_id)) is None
            assert len(manager._rooms.get(code, [])) == 1

            host_ws.receive_json()  # player_left
            # Jake's client ignores player_left and keeps reading. It gets the
            # close frame, then nothing -- not the next room event.
            jake_ws.receive_json()  # player_left, delivered before the close
            with pytest.raises(WebSocketDisconnect):
                jake_ws.receive_json()

        client.post(f"/rooms/{code}/join", json={"name": "Zoe"})
        # The post-kick event reaches the host and nobody else.
        assert host_ws.receive_json()["type"] == "player_joined"


def test_kick_closes_every_socket_a_player_holds(client):
    """A reconnect race can leave a stale socket open; both must be closed."""
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")

    with client.websocket_connect(f"/ws/{code}/{jake_id}"):
        with client.websocket_connect(f"/ws/{code}/{jake_id}"):
            assert len(manager._players[(code, jake_id)]) == 2
            client.post(
                f"/rooms/{code}/kick", json={"host_id": host_id, "player_id": jake_id}
            )
            assert manager._players.get((code, jake_id)) is None
            assert manager._rooms.get(code) is None


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


def test_heic_upload_is_rejected(client):
    # iOS shoots HEIC by default, but the Flutter client cannot decode HEIC when
    # the photo is served back, so the server must keep refusing it. The client
    # transcodes to JPEG at sample time instead (see lib/services/photo_sampler
    # .dart) — widening this allowlist would store photos nobody can display.
    # Real HEIC magic: an ISO-BMFF box with an `ftypheic` major brand at byte 4.
    heic = b"\x00\x00\x00\x18ftypheic\x00\x00\x00\x00heicmif1"
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")

    resp = _upload_photo(client, code, host_id, content=heic)
    assert resp.status_code == 400
    assert "JPEG or PNG" in resp.json()["detail"]


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


def test_fetching_a_photo_that_does_not_exist_is_404(client):
    # A real room, a well-formed filename, no such file: a miss must 404 and
    # not blow up on the missing path.
    code = client.post("/rooms").json()["code"]
    _join(client, code, "Emma")
    assert client.get(f"/rooms/{code}/photos/deadbeef1234.jpg").status_code == 404


def test_photos_of_an_unknown_room_are_404(client):
    assert client.get("/rooms/ZZZZZ/photos/deadbeef1234.jpg").status_code == 404


def test_upload_to_an_unknown_room_is_404(client):
    resp = _upload_photo(client, "ZZZZZ", "whoever")
    assert resp.status_code == 404


def test_upload_for_a_player_not_in_the_room_is_rejected(client):
    # owner_id is client-supplied. An unknown owner must not be able to plant
    # a photo nobody can be scored against.
    code = client.post("/rooms").json()["code"]
    _join(client, code, "Emma")
    resp = _upload_photo(client, code, "not-a-player")
    assert resp.status_code == 400
    assert client.get(f"/rooms/{code}").json()["players"][0]["photo_count"] == 0


def test_upload_without_an_owner_is_rejected(client):
    # owner_id is a required query param, not part of the multipart body.
    code = client.post("/rooms").json()["code"]
    _join(client, code, "Emma")
    files = {"file": ("photo.jpg", io.BytesIO(b"\xff\xd8\xff_fake_jpeg"), "image/jpeg")}
    resp = client.post(f"/rooms/{code}/photos", files=files)
    assert resp.status_code == 422


def test_upload_without_a_file_is_rejected(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    resp = client.post(f"/rooms/{code}/photos", params={"owner_id": host_id})
    assert resp.status_code == 422


def test_empty_upload_is_rejected(client):
    # A zero-byte file is caught by its own guard before the magic-byte check,
    # so the reason a player sees is "empty file", not "must be a JPEG or PNG".
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    resp = _upload_photo(client, code, host_id, content=b"")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "empty file"


def test_upload_with_a_non_image_content_type_is_rejected(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    files = {"file": ("photo.txt", io.BytesIO(b"\xff\xd8\xff_fake_jpeg"), "text/plain")}
    resp = client.post(
        f"/rooms/{code}/photos", params={"owner_id": host_id}, files=files
    )
    assert resp.status_code == 400


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


def test_websocket_for_an_unknown_room_is_refused(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/ZZZZZ/whoever") as ws:
            ws.receive_json()


def test_disconnecting_deregisters_the_socket(client):
    """A client that hangs up must leave nothing behind in the registry.

    Without the `finally` in the WS route the socket stays in the room list
    forever: every later broadcast writes to it, and the room dict grows for
    the process lifetime.
    """
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")

    with client.websocket_connect(f"/ws/{code}/{host_id}"):
        assert len(manager._rooms[code]) == 1
        assert len(manager._players[(code, host_id)]) == 1

    # Closing the last socket drops both entries, not just empties them.
    assert manager._rooms.get(code) is None
    assert manager._players.get((code, host_id)) is None


def test_one_client_disconnecting_leaves_the_others_connected(client):
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")
    jake_id = _join(client, code, "Jake")

    with client.websocket_connect(f"/ws/{code}/{host_id}") as host_ws:
        with client.websocket_connect(f"/ws/{code}/{jake_id}"):
            assert len(manager._rooms[code]) == 2
        assert len(manager._rooms[code]) == 1
        assert manager._players.get((code, jake_id)) is None

        # The surviving socket still gets events.
        _join(client, code, "Zoe")
        assert host_ws.receive_json()["type"] == "player_joined"


def test_broadcast_prunes_a_socket_that_died_without_disconnecting(client):
    """A socket that vanished without a close frame must not be written twice.

    A dropped connection (network gone, process killed) never reaches the
    route's `finally`, so the registry only learns it is dead when a send
    raises -- broadcast has to prune it there or every future broadcast keeps
    raising on the same corpse.
    """
    import anyio

    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")

    class DeadSocket:
        sends = 0

        async def send_json(self, message):
            DeadSocket.sends += 1
            raise RuntimeError("connection lost")

    dead = DeadSocket()
    manager._rooms.setdefault(code, []).append(dead)
    manager._players.setdefault((code, host_id), []).append(dead)

    anyio.run(manager.broadcast, code, {"type": "ping"})
    assert DeadSocket.sends == 1
    assert manager._rooms.get(code) is None
    assert manager._players.get((code, host_id)) is None

    # A second broadcast finds nothing to write to, rather than raising again.
    anyio.run(manager.broadcast, code, {"type": "ping"})
    assert DeadSocket.sends == 1


def test_broadcast_still_reaches_live_sockets_when_one_is_dead(client):
    # One dead peer must not cost everyone else their events -- rounds are
    # timed, so a swallowed broadcast loses real game time.
    code = client.post("/rooms").json()["code"]
    host_id = _join(client, code, "Emma")

    class DeadSocket:
        async def send_json(self, message):
            raise RuntimeError("connection lost")

    with client.websocket_connect(f"/ws/{code}/{host_id}") as host_ws:
        manager._rooms[code].insert(0, DeadSocket())
        _join(client, code, "Jake")

        assert host_ws.receive_json()["type"] == "player_joined"
        # The dead one was pruned; only the live socket is left.
        assert len(manager._rooms[code]) == 1


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
