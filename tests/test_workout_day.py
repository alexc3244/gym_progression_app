import pytest
from src.models.exercise import Exercise
from src.models.exercise_prescription import ExercisePrescription
from src.models.workout_day import WorkoutDay


# --- Helpers ---

@pytest.fixture
def prescription():
    # A minimal valid prescription reused across tests.
    exercise = Exercise(name="Smith Machine Bench Press", exercise_type="compound")
    return ExercisePrescription(
        exercise=exercise,
        sets=3,
        rep_min=8,
        rep_max=12,
        load_kg=80.0,
        rir_target=2,
    )

@pytest.fixture
def second_prescription():
    # A second distinct prescription for multi-exercise day tests.
    exercise = Exercise(name="Cable Lateral Raise", exercise_type="isolation")
    return ExercisePrescription(
        exercise=exercise,
        sets=3,
        rep_min=12,
        rep_max=15,
        load_kg=10.0,
        rir_target=2,
    )


# --- Valid construction ---

def test_valid_workout_day(prescription):
    # A valid name and non-empty prescriptions list should construct without errors.
    day = WorkoutDay(name="Push A", prescriptions=[prescription])
    assert day.name == "Push A"
    assert len(day.prescriptions) == 1

def test_multiple_prescriptions(prescription, second_prescription):
    # A day with multiple exercises should store all of them in order.
    day = WorkoutDay(name="Push A", prescriptions=[prescription, second_prescription])
    assert len(day.prescriptions) == 2
    assert day.prescriptions[0] == prescription
    assert day.prescriptions[1] == second_prescription


# --- Immutability ---

def test_prescriptions_list_is_copied(prescription):
    # Mutating the original list after construction should not affect
    # the WorkoutDay's internal prescriptions.
    original_list = [prescription]
    day = WorkoutDay(name="Push A", prescriptions=original_list)
    original_list.clear()
    assert len(day.prescriptions) == 1


# --- Validation ---

def test_empty_name(prescription):
    # An empty name cannot identify a workout day.
    with pytest.raises(ValueError):
        WorkoutDay(name="", prescriptions=[prescription])

def test_whitespace_name(prescription):
    # A whitespace-only name is functionally empty.
    with pytest.raises(ValueError):
        WorkoutDay(name="   ", prescriptions=[prescription])

def test_empty_prescriptions_list():
    # A workout day with no exercises is not valid.
    with pytest.raises(ValueError):
        WorkoutDay(name="Push A", prescriptions=[])

def test_invalid_prescriptions_type(prescription):
    # prescriptions must be a list, not another iterable type.
    with pytest.raises(TypeError):
        WorkoutDay(name="Push A", prescriptions=(prescription,))

def test_invalid_item_in_prescriptions(prescription):
    # Every item in the list must be an ExercisePrescription.
    # A raw string should be rejected.
    with pytest.raises(TypeError):
        WorkoutDay(name="Push A", prescriptions=[prescription, "not a prescription"])


# --- Dunder methods ---

def test_repr(prescription):
    # repr should include the day name and exercise count.
    day = WorkoutDay(name="Push A", prescriptions=[prescription])
    assert "Push A" in repr(day)
    assert "1" in repr(day)

def test_equality(prescription):
    # Two WorkoutDay instances with the same name and prescriptions should be equal.
    a = WorkoutDay(name="Push A", prescriptions=[prescription])
    b = WorkoutDay(name="Push A", prescriptions=[prescription])
    assert a == b

def test_inequality_different_name(prescription):
    # Same prescriptions but different name should not be equal.
    a = WorkoutDay(name="Push A", prescriptions=[prescription])
    b = WorkoutDay(name="Push B", prescriptions=[prescription])
    assert a != b
