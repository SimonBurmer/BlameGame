"""Unit tests for the Room state machine (app/game.py).

These tests describe the *rules* of the game with no server involved: joining,
starting, guessing, scoring, advancing rounds, and final rankings. Writing
them first forces us to design a clean, testable game API.
"""

import pytest

from app.models import RoomState
from app.game import (
    Room,
    GameError,
    add_player,
    remove_player,
    add_photo,
    start_game,
    submit_guess,
    advance_round,
    rankings,
    current_photo,
    reset_room,
)


def make_room() -> Room:
    return Room(code="TEST1")


# --- joining -------------------------------------------------------------

def test_first_player_becomes_host():
    room = make_room()
    p = add_player(room, "Emma")
    assert p.is_host is True
    assert p.name == "Emma"
    assert room.players == [p]


def test_second_player_is_not_host():
    room = make_room()
    add_player(room, "Emma")
    p2 = add_player(room, "Jake")
    assert p2.is_host is False


def test_duplicate_name_is_rejected():
    room = make_room()
    add_player(room, "Emma")
    with pytest.raises(GameError):
        add_player(room, "Emma")


def test_each_player_gets_a_unique_id():
    room = make_room()
    a = add_player(room, "Emma")
    b = add_player(room, "Jake")
    assert a.id != b.id


# --- photos + starting ---------------------------------------------------

def test_start_requires_at_least_two_players():
    room = make_room()
    emma = add_player(room, "Emma")
    add_photo(room, owner_id=emma.id, url="/uploads/1.jpg")
    with pytest.raises(GameError):
        start_game(room, total_rounds=3)


def test_start_requires_at_least_one_photo():
    room = make_room()
    add_player(room, "Emma")
    add_player(room, "Jake")
    with pytest.raises(GameError):
        start_game(room, total_rounds=3)


def test_start_requires_photos_from_two_different_players():
    # One player's photos would mean every round shows their pictures: they
    # recognise all of them and everyone else can only guess that one name.
    room = make_room()
    emma = add_player(room, "Emma")
    add_player(room, "Jake")
    add_photo(room, owner_id=emma.id, url="/uploads/1.jpg")
    add_photo(room, owner_id=emma.id, url="/uploads/2.jpg")
    with pytest.raises(GameError):
        start_game(room, total_rounds=3)


def test_start_builds_rounds_and_enters_in_round():
    room = make_room()
    emma = add_player(room, "Emma")
    jake = add_player(room, "Jake")
    add_photo(room, owner_id=emma.id, url="/uploads/1.jpg")
    add_photo(room, owner_id=jake.id, url="/uploads/2.jpg")
    start_game(room, total_rounds=2)
    assert room.state == RoomState.IN_ROUND
    assert len(room.rounds) == 2
    assert room.current_round == 0


def test_start_stores_round_seconds_on_the_room():
    room = make_room()
    emma = add_player(room, "Emma")
    jake = add_player(room, "Jake")
    add_photo(room, owner_id=emma.id, url="/uploads/1.jpg")
    add_photo(room, owner_id=jake.id, url="/uploads/2.jpg")
    start_game(room, total_rounds=1, round_seconds=15)
    assert room.round_seconds == 15


def test_cannot_start_twice():
    room = make_room()
    emma = add_player(room, "Emma")
    jake = add_player(room, "Jake")
    add_photo(room, owner_id=emma.id, url="/uploads/1.jpg")
    add_photo(room, owner_id=jake.id, url="/uploads/2.jpg")
    start_game(room, total_rounds=1)
    with pytest.raises(GameError):
        start_game(room, total_rounds=1)


# --- guessing + scoring --------------------------------------------------

# Fixed clock so scoring is deterministic: the server derives seconds_left
# from the round deadline rather than trusting a client-supplied number.
NOW = 1_000_000.0


def started_room(seconds_left: int = 8):
    """A room mid-game with a known current photo owned by Emma."""
    room = make_room()
    emma = add_player(room, "Emma")
    jake = add_player(room, "Jake")
    emma_photo = add_photo(room, owner_id=emma.id, url="/uploads/emma.jpg")
    add_photo(room, owner_id=jake.id, url="/uploads/jake.jpg")
    start_game(room, total_rounds=1)
    # start_game shuffles the pool, so pin the round to Emma's photo to keep
    # the expected owner deterministic.
    room.rounds[0].photo = emma_photo
    room.rounds[0].ends_at = NOW + seconds_left
    return room, emma, jake


def test_correct_guess_awards_points():
    room, emma, jake = started_room()
    # Jake correctly guesses Emma with 8 seconds left.
    points = submit_guess(room, guesser_id=jake.id, guessed_owner_id=emma.id, now=NOW)
    assert points == 800
    assert room.player_by_id(jake.id).score == 800


def test_wrong_guess_awards_nothing():
    room, emma, jake = started_room()
    points = submit_guess(room, guesser_id=jake.id, guessed_owner_id=jake.id, now=NOW)
    assert points == 0
    assert room.player_by_id(jake.id).score == 0


def test_player_cannot_guess_twice_in_a_round():
    room, emma, jake = started_room()
    submit_guess(room, guesser_id=jake.id, guessed_owner_id=emma.id, now=NOW)
    with pytest.raises(GameError):
        submit_guess(room, guesser_id=jake.id, guessed_owner_id=emma.id, now=NOW)


def test_guess_only_allowed_during_a_round():
    room, emma, jake = started_room()
    room.state = RoomState.REVEALING
    with pytest.raises(GameError):
        submit_guess(room, guesser_id=jake.id, guessed_owner_id=emma.id, now=NOW)


def test_current_photo_matches_first_round():
    room, emma, jake = started_room()
    assert current_photo(room).owner_id == emma.id


# --- advancing + results -------------------------------------------------

def test_advance_moves_to_next_round():
    room = make_room()
    emma = add_player(room, "Emma")
    jake = add_player(room, "Jake")
    add_photo(room, owner_id=emma.id, url="/uploads/1.jpg")
    add_photo(room, owner_id=jake.id, url="/uploads/2.jpg")
    start_game(room, total_rounds=2)
    advance_round(room)
    assert room.current_round == 1
    assert room.state == RoomState.IN_ROUND


def test_advance_past_last_round_finishes_game():
    room, emma, jake = started_room()  # total_rounds=1
    advance_round(room)
    assert room.state == RoomState.FINISHED


def test_rankings_sorted_by_score_desc():
    room, emma, jake = started_room()
    submit_guess(room, guesser_id=jake.id, guessed_owner_id=emma.id, now=NOW)  # jake 800
    ranked = rankings(room)
    assert [p.name for p in ranked] == ["Jake", "Emma"]
    assert ranked[0].score == 800


# --- resetting -------------------------------------------------------------

def test_reset_returns_finished_room_to_lobby():
    room, emma, jake = started_room()
    advance_round(room)  # total_rounds=1 -> FINISHED
    assert room.state == RoomState.FINISHED

    reset_room(room)

    assert room.state == RoomState.LOBBY
    assert room.rounds == []
    assert room.current_round == 0


def test_reset_keeps_players_and_code():
    room, emma, jake = started_room()
    submit_guess(room, guesser_id=jake.id, guessed_owner_id=emma.id, now=NOW)
    advance_round(room)

    reset_room(room)

    assert room.code == "TEST1"
    assert [p.name for p in room.players] == ["Emma", "Jake"]


def test_reset_carries_scores_over_to_the_next_round():
    room, emma, jake = started_room()
    submit_guess(room, guesser_id=jake.id, guessed_owner_id=emma.id, now=NOW)
    advance_round(room)

    reset_room(room)

    assert room.player_by_id(jake.id).score == 800


def test_reset_keeps_photos_for_the_next_round():
    room, emma, jake = started_room()
    advance_round(room)

    reset_room(room)

    # Both players' photos survive, so the group can play again without
    # re-uploading.
    assert len(room.photos) == 2


def test_reset_bumps_the_epoch():
    room, emma, jake = started_room()
    advance_round(room)
    before = room.epoch

    reset_room(room)

    # A rematch is a new game: any RoundDriver still alive from the finished
    # one must see a moved epoch and bow out instead of driving it.
    assert room.epoch > before


def test_reset_keeps_host():
    room, emma, jake = started_room()
    advance_round(room)

    reset_room(room)

    assert emma.is_host is True
    assert jake.is_host is False


def test_reset_mid_lobby_room_is_a_noop_state_change():
    room = make_room()
    add_player(room, "Emma")
    reset_room(room)
    assert room.state == RoomState.LOBBY


def test_cannot_reset_while_round_in_progress():
    room, emma, jake = started_room()
    assert room.state == RoomState.IN_ROUND
    with pytest.raises(GameError):
        reset_room(room)


def test_cannot_reset_while_revealing():
    room, emma, jake = started_room()
    room.state = RoomState.REVEALING
    with pytest.raises(GameError):
        reset_room(room)


# --- leaving / being removed ---------------------------------------------

def test_remove_player_drops_them_from_the_room():
    room = make_room()
    add_player(room, "Emma")
    jake = add_player(room, "Jake")

    remove_player(room, jake.id)

    assert room.player_by_id(jake.id) is None
    assert [p.name for p in room.players] == ["Emma"]


def test_remove_player_takes_their_photos_with_them():
    room = make_room()
    emma = add_player(room, "Emma")
    jake = add_player(room, "Jake")
    add_photo(room, owner_id=emma.id, url="/uploads/emma.jpg")
    add_photo(room, owner_id=jake.id, url="/uploads/jake.jpg")

    remove_player(room, jake.id)

    # Nobody can guess a departed player, so their photos can't stay in play.
    assert [p.owner_id for p in room.photos] == [emma.id]


def test_removing_the_host_hands_the_role_on():
    room = make_room()
    emma = add_player(room, "Emma")
    jake = add_player(room, "Jake")
    assert emma.is_host is True

    remove_player(room, emma.id)

    # Otherwise the room is left with nobody able to start or reset it.
    assert jake.is_host is True


def test_removing_the_last_player_leaves_an_empty_room():
    room = make_room()
    emma = add_player(room, "Emma")

    remove_player(room, emma.id)

    assert room.players == []


def test_remove_unknown_player_is_an_error():
    room = make_room()
    add_player(room, "Emma")
    with pytest.raises(GameError):
        remove_player(room, "nobody")


def test_removed_players_guess_stops_blocking_the_round():
    room, emma, jake = started_room()
    submit_guess(room, guesser_id=jake.id, guessed_owner_id=emma.id, now=NOW)
    assert room.rounds[0].guesses

    remove_player(room, jake.id)

    # A stale guess from someone who left would otherwise sit in the round.
    assert jake.id not in room.rounds[0].guesses


def test_pending_round_is_repointed_off_a_departed_players_photo():
    room = make_room()
    emma = add_player(room, "Emma")
    jake = add_player(room, "Jake")
    add_player(room, "Sam")
    emma_photo = add_photo(room, owner_id=emma.id, url="/uploads/emma.jpg")
    jake_photo = add_photo(room, owner_id=jake.id, url="/uploads/jake.jpg")
    start_game(room, total_rounds=2)
    room.rounds[0].photo = emma_photo
    room.rounds[1].photo = jake_photo

    remove_player(room, jake.id)

    # Round 1 hasn't been played yet, so it must not show a photo whose owner
    # is gone -- that round would be unwinnable for everyone.
    assert room.player_by_id(room.rounds[1].photo.owner_id) is not None


def test_already_played_round_keeps_its_photo():
    room = make_room()
    emma = add_player(room, "Emma")
    jake = add_player(room, "Jake")
    add_player(room, "Sam")
    jake_photo = add_photo(room, owner_id=jake.id, url="/uploads/jake.jpg")
    add_photo(room, owner_id=emma.id, url="/uploads/emma.jpg")
    start_game(room, total_rounds=2)
    room.rounds[0].photo = jake_photo
    advance_round(room)  # round 0 is done and scored

    remove_player(room, jake.id)

    # Rewriting a played round would rewrite history the players already saw.
    assert room.rounds[0].photo is jake_photo


def test_game_finishes_when_too_few_players_remain():
    room, emma, jake = started_room()

    remove_player(room, jake.id)

    # One player left is not a game; end it rather than run out the clock.
    assert room.state == RoomState.FINISHED


def test_game_finishes_when_the_last_photos_leave():
    room = make_room()
    emma = add_player(room, "Emma")
    jake = add_player(room, "Jake")
    add_player(room, "Sam")
    add_photo(room, owner_id=emma.id, url="/uploads/emma.jpg")
    add_photo(room, owner_id=jake.id, url="/uploads/jake.jpg")
    start_game(room, total_rounds=2)

    remove_player(room, emma.id)
    remove_player(room, jake.id)

    assert room.state == RoomState.FINISHED


def test_removing_in_the_lobby_does_not_finish_the_room():
    room = make_room()
    add_player(room, "Emma")
    jake = add_player(room, "Jake")

    remove_player(room, jake.id)

    assert room.state == RoomState.LOBBY


def test_scores_of_remaining_players_survive_a_removal():
    room, emma, jake = started_room()
    submit_guess(room, guesser_id=jake.id, guessed_owner_id=emma.id, now=NOW)
    jake_score = jake.score
    assert jake_score > 0

    remove_player(room, emma.id)

    # Removing someone must not disturb anyone else's running total.
    assert jake.score == jake_score
