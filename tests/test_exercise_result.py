import pytest
from src.models.exercise import Exercise
from src.models.exercise_prescription import ExercisePrescription
from src.models.set_result import SetResult
from src.models.exercise_result import ExerciseResult


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
def set_results():
    # Three valid set results reused across tests.
    return [
        SetResult(reps=10, load_kg=80.0, rpe=8.0),
        SetResult(reps=9, load_kg=80.0, rpe=8.5),
        SetResult(reps=9, load_kg=80.0, rpe=9.0),
    ]


# --- Valid construction ---

def test_valid_exercise_result(prescription, set_results):
    # A valid prescription and non-empty set_results list should
    # construct without errors and store all fields correctly.
    result = ExerciseResult(prescription=prescription, set_results=set_results)
    assert result.prescription == prescription
    assert len(result.set_results) == 3

def test_single_set_is_valid(prescription):
    # A single set result is a valid exercise result.
    result = ExerciseResult(
        prescription=prescription,
        set_results=[SetResult(reps=10, load_kg=80.0, rpe=8.0)]
    )
    assert result.total_sets_performed == 1


# --- Immutability ---

def test_set_results_list_is_copied(prescription, set_results):
    # Mutating the original list after construction should not affect
    # the ExerciseResult's internal set_results.
    original_list = list(set_results)
    result = ExerciseResult(prescription=prescription, set_results=original_list)
    original_list.clear()
    assert len(result.set_results) == 3


# --- Properties ---

def test_total_sets_performed(prescription, set_results):
    # total_sets_performed should equal the number of set results stored.
    result = ExerciseResult(prescription=prescription, set_results=set_results)
    assert result.total_sets_performed == 3

def test_average_rpe(prescription, set_results):
    # average_rpe should be the mean of all set RPE values.
    # (8.0 + 8.5 + 9.0) / 3 = 8.5
    result = ExerciseResult(prescription=prescription, set_results=set_results)
    assert result.average_rpe == pytest.approx(8.5)

def test_average_reps(prescription, set_results):
    # average_reps should be the mean of all set rep values.
    # (10 + 9 + 9) / 3 = 9.33...
    result = ExerciseResult(prescription=prescription, set_results=set_results)
    assert result.average_reps == pytest.approx(9.33, rel=1e-2)


# --- Validation ---

def test_invalid_prescription_type(set_results):
    # prescription must be an ExercisePrescription instance.
    with pytest.raises(TypeError):
        ExerciseResult(prescription="not a prescription", set_results=set_results)

def test_empty_set_results(prescription):
    # An exercise with no sets recorded was not performed.
    with pytest.raises(ValueError):
        ExerciseResult(prescription=prescription, set_results=[])

def test_invalid_set_results_type(prescription):
    # set_results must be a list, not another iterable type.
    with pytest.raises(TypeError):
        ExerciseResult(
            prescription=prescription,
            set_results=(SetResult(reps=10, load_kg=80.0, rpe=8.0),)
        )

def test_invalid_item_in_set_results(prescription):
    # Every item in the list must be a SetResult instance.
    with pytest.raises(TypeError):
        ExerciseResult(
            prescription=prescription,
            set_results=[SetResult(reps=10, load_kg=80.0, rpe=8.0), "not a set result"]
        )


# --- Dunder methods ---

def test_repr(prescription, set_results):
    # repr should include the exercise name, sets performed, and average RPE.
    result = ExerciseResult(prescription=prescription, set_results=set_results)
    assert "Smith Machine Bench Press" in repr(result)
    assert "3" in repr(result)

def test_equality(prescription, set_results):
    # Two ExerciseResult instances with identical fields should be equal.
    a = ExerciseResult(prescription=prescription, set_results=set_results)
    b = ExerciseResult(prescription=prescription, set_results=set_results)
    assert a == b

def test_inequality_different_set_results(prescription):
    # Different set results should not be equal.
    a = ExerciseResult(
        prescription=prescription,
        set_results=[SetResult(reps=10, load_kg=80.0, rpe=8.0)]
    )
    b = ExerciseResult(
        prescription=prescription,
        set_results=[SetResult(reps=8, load_kg=80.0, rpe=9.0)]
    )
    assert a != b
