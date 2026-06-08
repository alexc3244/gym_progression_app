import pytest
from datetime import date
from src.models.exercise import Exercise
from src.models.exercise_prescription import ExercisePrescription
from src.models.set_result import SetResult
from src.models.exercise_result import ExerciseResult
from src.models.workout_day import WorkoutDay
from src.models.workout_session import WorkoutSession


# --- Helpers ---

@pytest.fixture
def prescription():
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
    exercise = Exercise(name="Cable Lateral Raise", exercise_type="isolation")
    return ExercisePrescription(
        exercise=exercise,
        sets=3,
        rep_min=12,
        rep_max=15,
        load_kg=10.0,
        rir_target=2,
    )

@pytest.fixture
def exercise_result(prescription):
    return ExerciseResult(
        prescription=prescription,
        set_results=[
            SetResult(reps=10, load_kg=80.0, rpe=8.0),
            SetResult(reps=9, load_kg=80.0, rpe=8.5),
            SetResult(reps=9, load_kg=80.0, rpe=9.0),
        ]
    )

@pytest.fixture
def second_exercise_result(second_prescription):
    return ExerciseResult(
        prescription=second_prescription,
        set_results=[
            SetResult(reps=14, load_kg=10.0, rpe=7.0),
            SetResult(reps=13, load_kg=10.0, rpe=7.5),
            SetResult(reps=12, load_kg=10.0, rpe=8.0),
        ]
    )

@pytest.fixture
def workout_day(prescription):
    return WorkoutDay(name="Push A", prescriptions=[prescription])

@pytest.fixture
def session_date():
    return date(2026, 6, 4)


# --- Valid construction ---

def test_valid_session(workout_day, session_date, exercise_result):
    # A fully valid session should construct without errors
    # and store all fields correctly.
    session = WorkoutSession(
        workout_day=workout_day,
        session_date=session_date,
        exercise_results=[exercise_result],
    )
    assert session.workout_day == workout_day
    assert session.session_date == session_date
    assert len(session.exercise_results) == 1

def test_multiple_exercise_results(
    workout_day, session_date, exercise_result, second_exercise_result
):
    # A session with multiple exercise results should store all of them in order.
    session = WorkoutSession(
        workout_day=workout_day,
        session_date=session_date,
        exercise_results=[exercise_result, second_exercise_result],
    )
    assert session.total_exercises == 2


# --- Immutability ---

def test_exercise_results_list_is_copied(workout_day, session_date, exercise_result):
    # Mutating the original list after construction should not affect
    # the WorkoutSession's internal exercise_results.
    original_list = [exercise_result]
    session = WorkoutSession(
        workout_day=workout_day,
        session_date=session_date,
        exercise_results=original_list,
    )
    original_list.clear()
    assert len(session.exercise_results) == 1


# --- Properties ---

def test_total_exercises(workout_day, session_date, exercise_result):
    # total_exercises should equal the number of exercise results stored.
    session = WorkoutSession(
        workout_day=workout_day,
        session_date=session_date,
        exercise_results=[exercise_result],
    )
    assert session.total_exercises == 1

def test_average_session_rpe(
    workout_day, session_date, exercise_result, second_exercise_result
):
    # average_session_rpe should be the mean of all exercise average RPEs.
    # exercise_result avg RPE = (8.0 + 8.5 + 9.0) / 3 = 8.5
    # second_exercise_result avg RPE = (7.0 + 7.5 + 8.0) / 3 = 7.5
    # session average = (8.5 + 7.5) / 2 = 8.0
    session = WorkoutSession(
        workout_day=workout_day,
        session_date=session_date,
        exercise_results=[exercise_result, second_exercise_result],
    )
    assert session.average_session_rpe == pytest.approx(8.0)


# --- get_result_for_exercise ---

def test_get_result_for_exercise(workout_day, session_date, exercise_result):
    # Should return the ExerciseResult matching the given exercise name.
    session = WorkoutSession(
        workout_day=workout_day,
        session_date=session_date,
        exercise_results=[exercise_result],
    )
    result = session.get_result_for_exercise("Smith Machine Bench Press")
    assert result == exercise_result

def test_get_result_for_exercise_raises_for_unknown(
    workout_day, session_date, exercise_result
):
    # Should raise ValueError if no result exists for the given exercise name.
    session = WorkoutSession(
        workout_day=workout_day,
        session_date=session_date,
        exercise_results=[exercise_result],
    )
    with pytest.raises(ValueError):
        session.get_result_for_exercise("Squat")


# --- Validation ---

def test_invalid_workout_day_type(session_date, exercise_result):
    # workout_day must be a WorkoutDay instance.
    with pytest.raises(TypeError):
        WorkoutSession(
            workout_day="Push A",
            session_date=session_date,
            exercise_results=[exercise_result],
        )

def test_invalid_session_date_type(workout_day, exercise_result):
    # session_date must be a datetime.date instance.
    with pytest.raises(TypeError):
        WorkoutSession(
            workout_day=workout_day,
            session_date="2026-06-04",
            exercise_results=[exercise_result],
        )

def test_empty_exercise_results(workout_day, session_date):
    # A session with no exercise results was not a valid session.
    with pytest.raises(ValueError):
        WorkoutSession(
            workout_day=workout_day,
            session_date=session_date,
            exercise_results=[],
        )

def test_invalid_item_in_exercise_results(workout_day, session_date, exercise_result):
    # Every item in the list must be an ExerciseResult instance.
    with pytest.raises(TypeError):
        WorkoutSession(
            workout_day=workout_day,
            session_date=session_date,
            exercise_results=[exercise_result, "not a result"],
        )


# --- Dunder methods ---

def test_repr(workout_day, session_date, exercise_result):
    # repr should include the day name, date, and exercise count.
    session = WorkoutSession(
        workout_day=workout_day,
        session_date=session_date,
        exercise_results=[exercise_result],
    )
    assert "Push A" in repr(session)
    assert "2026-06-04" in repr(session)

def test_equality(workout_day, session_date, exercise_result):
    # Two sessions with identical fields should be equal.
    a = WorkoutSession(
        workout_day=workout_day,
        session_date=session_date,
        exercise_results=[exercise_result],
    )
    b = WorkoutSession(
        workout_day=workout_day,
        session_date=session_date,
        exercise_results=[exercise_result],
    )
    assert a == b

def test_inequality_different_date(workout_day, exercise_result):
    # Same day and results but different date should not be equal.
    a = WorkoutSession(
        workout_day=workout_day,
        session_date=date(2026, 6, 4),
        exercise_results=[exercise_result],
    )
    b = WorkoutSession(
        workout_day=workout_day,
        session_date=date(2026, 6, 5),
        exercise_results=[exercise_result],
    )
    assert a != b
