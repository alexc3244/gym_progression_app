import pytest
from src.models.exercise import Exercise
from src.models.exercise_prescription import ExercisePrescription


# --- Helpers ---

# Reusable exercise instance to avoid repeating construction across tests.
@pytest.fixture
def compound_exercise():
    return Exercise(name="Smith Machine Bench Press", exercise_type="compound")


# --- Valid construction ---

def test_valid_prescription(compound_exercise):
    # A fully valid prescription should be created without errors
    # and store all fields correctly.
    p = ExercisePrescription(
        exercise=compound_exercise,
        sets=3,
        rep_min=8,
        rep_max=12,
        load_kg=80.0,
        rir_target=2,
    )
    assert p.exercise == compound_exercise
    assert p.sets == 3
    assert p.rep_min == 8
    assert p.rep_max == 12
    assert p.load_kg == 80.0
    assert p.rir_target == 2

def test_rir_target_zero_is_valid(compound_exercise):
    # RIR of 0 means taken to failure - this is a legitimate prescription.
    p = ExercisePrescription(
        exercise=compound_exercise,
        sets=3,
        rep_min=8,
        rep_max=12,
        load_kg=80.0,
        rir_target=0,
    )
    assert p.rir_target == 0

def test_equal_rep_min_and_max_is_valid(compound_exercise):
    # A fixed rep target (e.g. 5x5) is valid - rep_min == rep_max is allowed.
    p = ExercisePrescription(
        exercise=compound_exercise,
        sets=5,
        rep_min=5,
        rep_max=5,
        load_kg=100.0,
        rir_target=2,
    )
    assert p.rep_min == p.rep_max


# --- Validation ---

def test_invalid_exercise_type():
    # exercise must be an Exercise instance, not a raw string or other type.
    with pytest.raises(TypeError):
        ExercisePrescription(
            exercise="Smith Machine Bench Press",
            sets=3,
            rep_min=8,
            rep_max=12,
            load_kg=80.0,
            rir_target=2,
        )

def test_sets_below_one(compound_exercise):
    # Zero or negative sets makes no physical sense.
    with pytest.raises(ValueError):
        ExercisePrescription(
            exercise=compound_exercise,
            sets=0,
            rep_min=8,
            rep_max=12,
            load_kg=80.0,
            rir_target=2,
        )

def test_rep_min_below_one(compound_exercise):
    # A rep target of zero or less is not a valid prescription.
    with pytest.raises(ValueError):
        ExercisePrescription(
            exercise=compound_exercise,
            sets=3,
            rep_min=0,
            rep_max=12,
            load_kg=80.0,
            rir_target=2,
        )

def test_rep_max_below_rep_min(compound_exercise):
    # rep_max less than rep_min is an incoherent rep range.
    with pytest.raises(ValueError):
        ExercisePrescription(
            exercise=compound_exercise,
            sets=3,
            rep_min=12,
            rep_max=8,
            load_kg=80.0,
            rir_target=2,
        )

def test_load_kg_zero(compound_exercise):
    # A load of zero is not a valid working weight.
    with pytest.raises(ValueError):
        ExercisePrescription(
            exercise=compound_exercise,
            sets=3,
            rep_min=8,
            rep_max=12,
            load_kg=0,
            rir_target=2,
        )

def test_negative_rir(compound_exercise):
    # RIR cannot be negative - it represents reps left in the tank.
    with pytest.raises(ValueError):
        ExercisePrescription(
            exercise=compound_exercise,
            sets=3,
            rep_min=8,
            rep_max=12,
            load_kg=80.0,
            rir_target=-1,
        )


# --- Dunder methods ---

def test_repr(compound_exercise):
    # repr should include the exercise name and key fields for readable output.
    p = ExercisePrescription(
        exercise=compound_exercise,
        sets=3,
        rep_min=8,
        rep_max=12,
        load_kg=80.0,
        rir_target=2,
    )
    assert "Smith Machine Bench Press" in repr(p)
    assert "80.0" in repr(p)

def test_equality(compound_exercise):
    # Two prescriptions with identical fields should be equal.
    a = ExercisePrescription(
        exercise=compound_exercise, sets=3, rep_min=8, rep_max=12, load_kg=80.0, rir_target=2
    )
    b = ExercisePrescription(
        exercise=compound_exercise, sets=3, rep_min=8, rep_max=12, load_kg=80.0, rir_target=2
    )
    assert a == b

def test_inequality_different_load(compound_exercise):
    # A prescription with a different load should not be equal.
    a = ExercisePrescription(
        exercise=compound_exercise, sets=3, rep_min=8, rep_max=12, load_kg=80.0, rir_target=2
    )
    b = ExercisePrescription(
        exercise=compound_exercise, sets=3, rep_min=8, rep_max=12, load_kg=82.5, rir_target=2
    )
    assert a != b
