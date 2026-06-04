import pytest
from src.models.exercise import Exercise
from src.models.exercise_prescription import ExercisePrescription
from src.models.workout_day import WorkoutDay
from src.models.program import Program


# --- Helpers ---

@pytest.fixture
def prescription():
    # Minimal valid prescription reused across tests.
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
def push_a(prescription):
    return WorkoutDay(name="Push A", prescriptions=[prescription])

@pytest.fixture
def push_b(prescription):
    return WorkoutDay(name="Push B", prescriptions=[prescription])


# --- Valid construction ---

def test_valid_program(push_a):
    # A valid name and non-empty workout_days list should construct without errors.
    programme = Program(name="PPL Hypertrophy Block 1", workout_days=[push_a])
    assert programme.name == "PPL Hypertrophy Block 1"
    assert len(programme.workout_days) == 1

def test_multiple_days(push_a, push_b):
    # A programme with multiple days should store all of them in order.
    programme = Program(name="PPL Hypertrophy Block 1", workout_days=[push_a, push_b])
    assert len(programme.workout_days) == 2
    assert programme.workout_days[0] == push_a
    assert programme.workout_days[1] == push_b


# --- Immutability ---

def test_workout_days_list_is_copied(push_a):
    # Mutating the original list after construction should not affect
    # the Programme's internal workout_days.
    original_list = [push_a]
    programme = Program(name="PPL Hypertrophy Block 1", workout_days=original_list)
    original_list.clear()
    assert len(programme.workout_days) == 1


# --- get_day ---

def test_get_day_returns_correct_day(push_a, push_b):
    # get_day should return the WorkoutDay matching the given name.
    programme = Program(name="PPL Hypertrophy Block 1", workout_days=[push_a, push_b])
    assert programme.get_day("Push B") == push_b

def test_get_day_raises_for_unknown_name(push_a):
    # get_day should raise ValueError if no day with that name exists.
    programme = Program(name="PPL Hypertrophy Block 1", workout_days=[push_a])
    with pytest.raises(ValueError):
        programme.get_day("Legs A")


# --- Validation ---

def test_empty_name(push_a):
    # An empty name cannot identify a programme.
    with pytest.raises(ValueError):
        Program(name="", workout_days=[push_a])

def test_whitespace_name(push_a):
    # A whitespace-only name is functionally empty.
    with pytest.raises(ValueError):
        Program(name="   ", workout_days=[push_a])

def test_empty_workout_days():
    # A programme with no days is not valid.
    with pytest.raises(ValueError):
        Program(name="PPL Hypertrophy Block 1", workout_days=[])

def test_invalid_workout_days_type(push_a):
    # workout_days must be a list, not another iterable type.
    with pytest.raises(TypeError):
        Program(name="PPL Hypertrophy Block 1", workout_days=(push_a,))

def test_invalid_item_in_workout_days(push_a):
    # Every item in the list must be a WorkoutDay instance.
    with pytest.raises(TypeError):
        Program(name="PPL Hypertrophy Block 1", workout_days=[push_a, "not a day"])


# --- Dunder methods ---

def test_repr(push_a):
    # repr should include the programme name and day count.
    programme = Program(name="PPL Hypertrophy Block 1", workout_days=[push_a])
    assert "PPL Hypertrophy Block 1" in repr(programme)
    assert "1" in repr(programme)

def test_equality(push_a):
    # Two Programme instances with the same name and days should be equal.
    a = Program(name="PPL Hypertrophy Block 1", workout_days=[push_a])
    b = Program(name="PPL Hypertrophy Block 1", workout_days=[push_a])
    assert a == b

def test_inequality_different_name(push_a):
    # Same days but different name should not be equal.
    a = Program(name="PPL Hypertrophy Block 1", workout_days=[push_a])
    b = Program(name="PPL Hypertrophy Block 2", workout_days=[push_a])
    assert a != b
