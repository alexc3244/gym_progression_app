import pytest
from datetime import date
from src.models.exercise import Exercise
from src.models.exercise_prescription import ExercisePrescription
from src.models.set_result import SetResult
from src.models.exercise_result import ExerciseResult
from src.models.workout_day import WorkoutDay
from src.models.workout_session import WorkoutSession
from src.models.program import Program
from src.engine.progression import evaluate_session


# --- Helpers ---

def make_prescription(name, exercise_type, rep_min, rep_max, load_kg, rir_target=2):
    # Builds an ExercisePrescription from minimal arguments.
    exercise = Exercise(name=name, exercise_type=exercise_type)
    return ExercisePrescription(
        exercise=exercise,
        sets=3,
        rep_min=rep_min,
        rep_max=rep_max,
        load_kg=load_kg,
        rir_target=rir_target,
    )

def make_result(prescription, reps_per_set, rpe_per_set):
    # Builds an ExerciseResult from a list of reps and RPEs per set.
    set_results = [
        SetResult(reps=r, load_kg=prescription.load_kg, rpe=e)
        for r, e in zip(reps_per_set, rpe_per_set)
    ]
    return ExerciseResult(prescription=prescription, set_results=set_results)

def make_session(prescription, exercise_result):
    # Builds a minimal WorkoutSession from a single exercise result.
    workout_day = WorkoutDay(name="Push A", prescriptions=[prescription])
    return WorkoutSession(
        workout_day=workout_day,
        session_date=date(2026, 6, 16),
        exercise_results=[exercise_result],
    )

def make_program(prescription):
    # Builds a minimal Program from a single prescription.
    workout_day = WorkoutDay(name="Push A", prescriptions=[prescription])
    return Program(name="PPL Block 1", workout_days=[workout_day])


# --- Increase decisions ---

def test_increase_above_range_optimal_rpe():
    # Reps above range at optimal RPE should trigger an increase.
    # Compound: +2.5kg
    p = make_prescription("Bench Press", "compound", rep_min=8, rep_max=12, load_kg=80.0)
    result = make_result(p, reps_per_set=[13, 13, 12], rpe_per_set=[8.0, 8.0, 8.0])
    session = make_session(p, result)
    program = make_program(p)

    decisions = evaluate_session(session, program)

    assert len(decisions) == 1
    assert decisions[0].outcome == "increase"
    assert decisions[0].new_load_kg == 82.5

def test_increase_isolation_above_range_optimal_rpe():
    # Isolation exercise above range should use the smaller increment.
    # Isolation: +1.25kg
    p = make_prescription("Cable Lateral Raise", "isolation", rep_min=12, rep_max=15, load_kg=10.0)
    result = make_result(p, reps_per_set=[16, 16, 15], rpe_per_set=[7.5, 7.5, 8.0])
    session = make_session(p, result)
    program = make_program(p)

    decisions = evaluate_session(session, program)

    assert decisions[0].outcome == "increase"
    assert decisions[0].new_load_kg == 11.25

def test_increase_triggered_by_too_easy_rpe():
    # Reps in range but RPE < 7.0 should accelerate to increase.
    p = make_prescription("Bench Press", "compound", rep_min=8, rep_max=12, load_kg=80.0)
    result = make_result(p, reps_per_set=[10, 10, 10], rpe_per_set=[6.0, 6.5, 6.5])
    session = make_session(p, result)
    program = make_program(p)

    decisions = evaluate_session(session, program)

    assert decisions[0].outcome == "increase"
    assert "too easy" in decisions[0].reason.lower()


# --- Maintain decisions ---

def test_maintain_in_range_optimal_rpe():
    # Reps in range at optimal RPE should maintain load.
    p = make_prescription("Bench Press", "compound", rep_min=8, rep_max=12, load_kg=80.0)
    result = make_result(p, reps_per_set=[10, 10, 9], rpe_per_set=[8.0, 8.0, 8.5])
    session = make_session(p, result)
    program = make_program(p)

    decisions = evaluate_session(session, program)

    assert decisions[0].outcome == "maintain"
    assert decisions[0].new_load_kg == 80.0

def test_maintain_above_range_hard_rpe():
    # Reps above range but RPE 8.6-9.5 should be pulled back to maintain.
    p = make_prescription("Bench Press", "compound", rep_min=8, rep_max=12, load_kg=80.0)
    result = make_result(p, reps_per_set=[13, 13, 13], rpe_per_set=[9.0, 9.0, 9.0])
    session = make_session(p, result)
    program = make_program(p)

    decisions = evaluate_session(session, program)

    assert decisions[0].outcome == "maintain"
    assert "conservative" in decisions[0].reason.lower()


# --- Decrease decisions ---

def test_decrease_below_range_optimal_rpe():
    # Reps below range should trigger a decrease.
    p = make_prescription("Bench Press", "compound", rep_min=8, rep_max=12, load_kg=80.0)
    result = make_result(p, reps_per_set=[6, 6, 7], rpe_per_set=[8.0, 8.5, 8.5])
    session = make_session(p, result)
    program = make_program(p)

    decisions = evaluate_session(session, program)

    assert decisions[0].outcome == "decrease"
    assert decisions[0].new_load_kg == 77.5

def test_decrease_triggered_by_maximal_rpe():
    # RPE > 9.5 should override to decrease regardless of reps.
    p = make_prescription("Bench Press", "compound", rep_min=8, rep_max=12, load_kg=80.0)
    result = make_result(p, reps_per_set=[12, 11, 10], rpe_per_set=[9.8, 9.8, 9.8])
    session = make_session(p, result)
    program = make_program(p)

    decisions = evaluate_session(session, program)

    assert decisions[0].outcome == "decrease"
    assert "maximal" in decisions[0].reason.lower()


# --- Multiple exercises ---

def test_multiple_exercises_returns_one_decision_each():
    # A session with two exercises should return two decisions.
    p1 = make_prescription("Bench Press", "compound", rep_min=8, rep_max=12, load_kg=80.0)
    p2 = make_prescription("Cable Lateral Raise", "isolation", rep_min=12, rep_max=15, load_kg=10.0)

    r1 = make_result(p1, reps_per_set=[13, 13, 12], rpe_per_set=[8.0, 8.0, 8.0])
    r2 = make_result(p2, reps_per_set=[13, 13, 13], rpe_per_set=[7.5, 7.5, 8.0])

    workout_day = WorkoutDay(name="Push A", prescriptions=[p1, p2])
    session = WorkoutSession(
        workout_day=workout_day,
        session_date=date(2026, 6, 16),
        exercise_results=[r1, r2],
    )
    program = Program(
        name="PPL Block 1",
        workout_days=[workout_day],
    )

    decisions = evaluate_session(session, program)

    assert len(decisions) == 2
    assert decisions[0].exercise.name == "Bench Press"
    assert decisions[1].exercise.name == "Cable Lateral Raise"


# --- Reason strings ---

def test_reason_string_is_populated():
    # Every decision should have a non-empty reason string.
    p = make_prescription("Bench Press", "compound", rep_min=8, rep_max=12, load_kg=80.0)
    result = make_result(p, reps_per_set=[10, 10, 10], rpe_per_set=[8.0, 8.0, 8.0])
    session = make_session(p, result)
    program = make_program(p)

    decisions = evaluate_session(session, program)

    assert decisions[0].reason != ""
