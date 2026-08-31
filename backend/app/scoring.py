"""Pure scoring logic for Photo Blame.

Kept deliberately free of any framework, model, or I/O code so it is trivial
to unit-test. This mirrors the rule the Flutter app used inline
(`_timeLeft * 100`), now extracted into one tested place.
"""

POINTS_PER_SECOND = 100


def points_for_guess(*, correct: bool, seconds_left: int) -> int:
    """Points earned for a single guess.

    A correct guess is worth ``seconds_left * POINTS_PER_SECOND`` — faster
    answers score more. A wrong guess, or no time left, scores nothing.
    Never returns a negative value.
    """
    if not correct or seconds_left <= 0:
        return 0
    return seconds_left * POINTS_PER_SECOND
