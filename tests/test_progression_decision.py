import pytest
from src.models.exercise import Exercise
from src.models.progression_decision import ProgressionDecision


# --- Helpers ---

@pytest.fixture
def compound_exercise():
    return Exercise(name="Smith Machine Bench Press", exercise_type="compound")


# --- Valid construction ---

def test_valid_increase(compound_exercise):
    # An increase decision with a higher new load should construct without errors.
    d = ProgressionDecision(
        exercise=compound_exercise,
        current_load_kg=80.0,
        new_load_kg=82.5,
        outcome="increase",
        reason="Top of rep range achieved across all sets.",
    )
    assert d.outcome == "increase"
    assert d.new_load_kg == 82.5

def test_valid_maintain(compound_exercise):
    # A maintain decision with unchanged load should construct without errors.
    d = ProgressionDecision(
        exercise=compound_exercise,
        current_load_kg=80.0,
        new_load_kg=80.0,
        outcome="maintain",
        reason="Rep target not fully met. Maintain load.",
    )
    assert d.outcome == "maintain"
    assert d.load_change_kg == 0.0

def test_valid_decrease(compound_exercise):
    # A decrease decision with a lower new load should construct without errors.
    d = ProgressionDecision(
        exercise=compound_exercise,
        current_load_kg=80.0,
        new_load_kg=75.0,
        outcome="decrease",
        reason="Missed minimum reps on all sets. Reduce load.",
    )
    assert d.outcome == "decrease"
    assert d.new_load_kg == 75.0


# --- load_change_kg property ---

def test_load_change_positive_for_increase(compound_exercise):
    # load_change_kg should be positive for an increase decision.
    d = ProgressionDecision(
        exercise=compound_exercise,
        current_load_kg=80.0,
        new_load_kg=82.5,
        outcome="increase",
        reason="Top of rep range achieved.",
    )
    assert d.load_change_kg == pytest.approx(2.5)

def test_load_change_zero_for_maintain(compound_exercise):
    # load_change_kg should be zero for a maintain decision.
    d = ProgressionDecision(
        exercise=compound_exercise,
        current_load_kg=80.0,
        new_load_kg=80.0,
        outcome="maintain",
        reason="Rep target not met.",
    )
    assert d.load_change_kg == 0.0

def test_load_change_negative_for_decrease(compound_exercise):
    # load_change_kg should be negative for a decrease decision.
    d = ProgressionDecision(
        exercise=compound_exercise,
        current_load_kg=80.0,
        new_load_kg=75.0,
        outcome="decrease",
        reason="Missed minimum reps.",
    )
    assert d.load_change_kg == pytest.approx(-5.0)


# --- Consistency validation ---

def test_increase_with_same_load_rejected(compound_exercise):
    # An increase outcome with unchanged load is internally inconsistent.
    with pytest.raises(ValueError):
        ProgressionDecision(
            exercise=compound_exercise,
            current_load_kg=80.0,
            new_load_kg=80.0,
            outcome="increase",
            reason="Top of rep range achieved.",
        )

def test_increase_with_lower_load_rejected(compound_exercise):
    # An increase outcome with a lower new load is internally inconsistent.
    with pytest.raises(ValueError):
        ProgressionDecision(
            exercise=compound_exercise,
            current_load_kg=80.0,
            new_load_kg=77.5,
            outcome="increase",
            reason="Top of rep range achieved.",
        )

def test_decrease_with_same_load_rejected(compound_exercise):
    # A decrease outcome with unchanged load is internally inconsistent.
    with pytest.raises(ValueError):
        ProgressionDecision(
            exercise=compound_exercise,
            current_load_kg=80.0,
            new_load_kg=80.0,
            outcome="decrease",
            reason="Missed minimum reps.",
        )

def test_maintain_with_different_load_rejected(compound_exercise):
    # A maintain outcome with a changed load is internally inconsistent.
    with pytest.raises(ValueError):
        ProgressionDecision(
            exercise=compound_exercise,
            current_load_kg=80.0,
            new_load_kg=82.5,
            outcome="maintain",
            reason="Rep target not met.",
        )


# --- Field validation ---

def test_invalid_exercise_type():
    # exercise must be an Exercise instance.
    with pytest.raises(TypeError):
        ProgressionDecision(
            exercise="Smith Machine Bench Press",
            current_load_kg=80.0,
            new_load_kg=82.5,
            outcome="increase",
            reason="Top of rep range achieved.",
        )

def test_invalid_outcome(compound_exercise):
    # outcome must be one of the three permitted values.
    with pytest.raises(ValueError):
        ProgressionDecision(
            exercise=compound_exercise,
            current_load_kg=80.0,
            new_load_kg=82.5,
            outcome="deload",
            reason="Fatigue accumulation.",
        )

def test_empty_reason(compound_exercise):
    # reason cannot be empty - explainability is a core requirement.
    with pytest.raises(ValueError):
        ProgressionDecision(
            exercise=compound_exercise,
            current_load_kg=80.0,
            new_load_kg=82.5,
            outcome="increase",
            reason="",
        )

def test_negative_current_load(compound_exercise):
    with pytest.raises(ValueError):
        ProgressionDecision(
            exercise=compound_exercise,
            current_load_kg=-80.0,
            new_load_kg=82.5,
            outcome="increase",
            reason="Top of rep range achieved.",
        )


# --- Dunder methods ---

def test_repr(compound_exercise):
    # repr should include exercise name, outcome, and both loads.
    d = ProgressionDecision(
        exercise=compound_exercise,
        current_load_kg=80.0,
        new_load_kg=82.5,
        outcome="increase",
        reason="Top of rep range achieved.",
    )
    assert "Smith Machine Bench Press" in repr(d)
    assert "increase" in repr(d)
    assert "80.0" in repr(d)
    assert "82.5" in repr(d)

def test_equality(compound_exercise):
    # Two decisions with identical fields should be equal.
    a = ProgressionDecision(
        exercise=compound_exercise,
        current_load_kg=80.0,
        new_load_kg=82.5,
        outcome="increase",
        reason="Top of rep range achieved.",
    )
    b = ProgressionDecision(
        exercise=compound_exercise,
        current_load_kg=80.0,
        new_load_kg=82.5,
        outcome="increase",
        reason="Top of rep range achieved.",
    )
    assert a == b

def test_inequality_different_outcome(compound_exercise):
    # Same exercise and loads but different outcome should not be equal.
    a = ProgressionDecision(
        exercise=compound_exercise,
        current_load_kg=80.0,
        new_load_kg=80.0,
        outcome="maintain",
        reason="Rep target not met.",
    )
    b = ProgressionDecision(
        exercise=compound_exercise,
        current_load_kg=80.0,
        new_load_kg=82.5,
        outcome="increase",
        reason="Top of rep range achieved.",
    )
    assert a != b
