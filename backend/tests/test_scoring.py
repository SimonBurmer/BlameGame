"""Unit tests for the pure scoring logic.

This is the classic place to start TDD: a pure function with no I/O, no
network, no database. Each test is a plain function whose name starts with
`test_`; pytest discovers them automatically. `assert` checks the result.
"""

from app.scoring import points_for_guess, POINTS_PER_SECOND


def test_correct_guess_awards_time_bonus():
    # 7 seconds left, correct guess -> 7 * 100 = 700 points
    assert points_for_guess(correct=True, seconds_left=7) == 700


def test_correct_guess_with_no_time_left_scores_zero():
    assert points_for_guess(correct=True, seconds_left=0) == 0


def test_wrong_guess_scores_zero_regardless_of_time():
    assert points_for_guess(correct=False, seconds_left=9) == 0


def test_points_are_never_negative():
    # Defensive: negative time should never produce negative points.
    assert points_for_guess(correct=True, seconds_left=-3) == 0


def test_points_per_second_constant_is_used():
    # One second left should be worth exactly POINTS_PER_SECOND.
    assert points_for_guess(correct=True, seconds_left=1) == POINTS_PER_SECOND
