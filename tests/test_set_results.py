import pytest
from src.models.set_result import SetResult


# --- Valid construction ---

def test_valid_set_result():
    # A fully valid set result should construct without errors
    # and store all fields correctly.
    s = SetResult(reps=10, load_kg=80.0, rpe=8.0)
    assert s.reps == 10
    assert s.load_kg == 80.0
    assert s.rpe == 8.0

def test_half_point_rpe():
    # Half-point RPE values are common in practice and should be accepted.
    s = SetResult(reps=10, load_kg=80.0, rpe=7.5)
    assert s.rpe == 7.5

def test_rpe_boundary_low():
    # RPE of 1.0 is the minimum valid value.
    s = SetResult(reps=10, load_kg=80.0, rpe=1.0)
    assert s.rpe == 1.0

def test_rpe_boundary_high():
    # RPE of 10.0 means maximal effort - should be accepted.
    s = SetResult(reps=10, load_kg=80.0, rpe=10.0)
    assert s.rpe == 10.0


# --- RIR property ---

def test_rir_derived_from_rpe():
    # RIR should always equal 10 - RPE.
    s = SetResult(reps=10, load_kg=80.0, rpe=8.0)
    assert s.rir == 2.0

def test_rir_at_failure():
    # RPE 10 means failure - RIR should be 0.
    s = SetResult(reps=10, load_kg=80.0, rpe=10.0)
    assert s.rir == 0.0


# --- Validation ---

def test_reps_below_one():
    # Zero or negative reps means the set was not performed.
    with pytest.raises(ValueError):
        SetResult(reps=0, load_kg=80.0, rpe=8.0)

def test_load_kg_zero():
    # A load of zero is not a valid working weight.
    with pytest.raises(ValueError):
        SetResult(reps=10, load_kg=0, rpe=8.0)

def test_load_kg_negative():
    # Negative load is physically meaningless.
    with pytest.raises(ValueError):
        SetResult(reps=10, load_kg=-10.0, rpe=8.0)

def test_rpe_below_minimum():
    # RPE below 1.0 is outside the valid Borg scale range.
    with pytest.raises(ValueError):
        SetResult(reps=10, load_kg=80.0, rpe=0.0)

def test_rpe_above_maximum():
    # RPE above 10.0 is outside the valid Borg scale range.
    with pytest.raises(ValueError):
        SetResult(reps=10, load_kg=80.0, rpe=11.0)


# --- Dunder methods ---

def test_repr():
    # repr should include reps, load, rpe, and derived rir.
    s = SetResult(reps=10, load_kg=80.0, rpe=8.0)
    assert "10" in repr(s)
    assert "80.0" in repr(s)
    assert "8.0" in repr(s)
    assert "2.0" in repr(s)

def test_equality():
    # Two set results with identical fields should be equal.
    a = SetResult(reps=10, load_kg=80.0, rpe=8.0)
    b = SetResult(reps=10, load_kg=80.0, rpe=8.0)
    assert a == b

def test_inequality_different_reps():
    # Different reps should not be equal.
    a = SetResult(reps=10, load_kg=80.0, rpe=8.0)
    b = SetResult(reps=9, load_kg=80.0, rpe=8.0)
    assert a != b

def test_inequality_different_rpe():
    # Different RPE should not be equal.
    a = SetResult(reps=10, load_kg=80.0, rpe=8.0)
    b = SetResult(reps=10, load_kg=80.0, rpe=9.0)
    assert a != b
