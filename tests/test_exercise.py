import pytest
from src.models.exercise import Exercise


# --- Valid construction ---

def test_valid_compound():
    # A compound exercise should be created without errors
    # and store both fields correctly.
    e = Exercise(name="Smith Machine Bench Press", exercise_type="compound")
    assert e.name == "Smith Machine Bench Press"
    assert e.exercise_type == "compound"

def test_valid_isolation():
    # Isolation is the second permitted type - verify it is accepted.
    e = Exercise(name="Cable Lateral Raise", exercise_type="isolation")
    assert e.exercise_type == "isolation"


# --- Validation ---

def test_invalid_exercise_type():
    # Any value outside the controlled vocabulary should raise ValueError.
    # Protects the progression engine from receiving an unknown type.
    with pytest.raises(ValueError):
        Exercise(name="Squat", exercise_type="cardio")

def test_empty_name():
    # An empty name would make exercise lookups during logging unreliable.
    with pytest.raises(ValueError):
        Exercise(name="", exercise_type="compound")

def test_whitespace_name():
    # A name of only whitespace is functionally empty - should also be rejected.
    with pytest.raises(ValueError):
        Exercise(name="   ", exercise_type="compound")


# --- Dunder methods ---

def test_repr():
    # repr should include the exercise name for readable debug output.
    e = Exercise(name="Squat", exercise_type="compound")
    assert "Squat" in repr(e)

def test_equality():
    # Two exercises with identical fields should be considered equal.
    a = Exercise(name="Squat", exercise_type="compound")
    b = Exercise(name="Squat", exercise_type="compound")
    assert a == b

def test_inequality_different_type():
    # Same name but different type should not be equal.
    a = Exercise(name="Squat", exercise_type="compound")
    b = Exercise(name="Squat", exercise_type="isolation")
    assert a != b

def test_inequality_different_name():
    # Same type but different name should not be equal.
    a = Exercise(name="Squat", exercise_type="compound")
    b = Exercise(name="Leg Press", exercise_type="compound")
    assert a != b
