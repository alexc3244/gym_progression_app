import pytest
from datetime import date
from src.models.exercise import Exercise
from src.models.exercise_prescription import ExercisePrescription
from src.models.set_result import SetResult
from src.models.exercise_result import ExerciseResult
from src.models.workout_day import WorkoutDay
from src.models.workout_session import WorkoutSession
from src.models.program import Program
from src.services.session_service import SessionService


# --- Helpers ---

def make_prescription(name, exercise_type, rep_min, rep_max, load_kg):
    exercise = Exercise(name=name, exercise_type=exercise_type)
    return ExercisePrescription(
        exercise=exercise,
        sets=3,
        rep_min=rep_min,
        rep_max=rep_max,
        load_kg=load_kg,
        rir_target=2,
    )

def make_result(prescription, reps_per_set, rpe_per_set):
    set_results = [
        SetResult(reps=r, load_kg=prescription.load_kg, rpe=e)
        for r, e in zip(reps_per_set, rpe_per_set)
    ]
    return ExerciseResult(prescription=prescription, set_results=set_results)


# --- Fixtures ---

@pytest.fixture
def service():
    return SessionService()

@pytest.fixture
def bench_prescription():
    return make_prescription("Bench Press", "compound", rep_min=8, rep_max=12, load_kg=80.0)

@pytest.fixture
def lateral_prescription():
    return make_prescription("Cable Lateral Raise", "isolation", rep_min=12, rep_max=15, load_kg=10.0)

@pytest.fixture
def program(bench_prescription, lateral_prescription):
    day = WorkoutDay(name="Push A", prescriptions=[bench_prescription, lateral_prescription])
    return Program(name="PPL Block 1", workout_days=[day])

@pytest.fixture
def session_above_range(bench_prescription, lateral_prescription):
    # Both exercises performed above rep range at optimal RPE.
    # Expected: both loads increase.
    bench_result = make_result(
        bench_prescription,
        reps_per_set=[13, 13, 13],
        rpe_per_set=[8.0, 8.0, 8.0],
    )
    lateral_result = make_result(
        lateral_prescription,
        reps_per_set=[16, 16, 16],
        rpe_per_set=[7.5, 7.5, 7.5],
    )
    day = WorkoutDay(
        name="Push A",
        prescriptions=[bench_prescription, lateral_prescription],
    )
    return WorkoutSession(
        workout_day=day,
        session_date=date(2026, 6, 16),
        exercise_results=[bench_result, lateral_result],
    )


# --- process_session ---

def test_process_session_returns_decisions_and_updated_program(
    service, session_above_range, program
):
    # process_session should return a tuple of decisions and updated program.
    decisions, updated_program = service.process_session(session_above_range, program)

    assert isinstance(decisions, list)
    assert isinstance(updated_program, Program)

def test_process_session_returns_one_decision_per_exercise(
    service, session_above_range, program
):
    # One decision should be returned per exercise in the session.
    decisions, _ = service.process_session(session_above_range, program)
    assert len(decisions) == 2

def test_process_session_increases_loads_when_above_range(
    service, session_above_range, program
):
    # Both exercises above range should result in increased loads in the
    # updated programme.
    _, updated_program = service.process_session(session_above_range, program)

    updated_day = updated_program.get_day("Push A")
    bench = next(
        p for p in updated_day.prescriptions if p.exercise.name == "Bench Press"
    )
    lateral = next(
        p for p in updated_day.prescriptions if p.exercise.name == "Cable Lateral Raise"
    )

    assert bench.load_kg == 82.5       # compound +2.5kg
    assert lateral.load_kg == 11.25    # isolation +1.25kg


# --- Immutability ---

def test_original_program_not_mutated(service, session_above_range, program):
    # The original program should not be modified by process_session.
    original_bench_load = (
        program.get_day("Push A").prescriptions[0].load_kg
    )

    service.process_session(session_above_range, program)

    bench_load_after = (
        program.get_day("Push A").prescriptions[0].load_kg
    )
    assert bench_load_after == original_bench_load


# --- Partial session (subset of exercises) ---

def test_unexercised_prescriptions_carry_over_unchanged(
    service, program, bench_prescription
):
    # If a session only covers one exercise, the other prescription in the
    # programme should carry over with its original load unchanged.
    bench_result = make_result(
        bench_prescription,
        reps_per_set=[13, 13, 13],
        rpe_per_set=[8.0, 8.0, 8.0],
    )
    day = WorkoutDay(name="Push A", prescriptions=[bench_prescription])
    session = WorkoutSession(
        workout_day=day,
        session_date=date(2026, 6, 16),
        exercise_results=[bench_result],
    )

    _, updated_program = service.process_session(session, program)

    updated_day = updated_program.get_day("Push A")
    lateral = next(
        p for p in updated_day.prescriptions if p.exercise.name == "Cable Lateral Raise"
    )

    # Cable Lateral Raise was not in the session - load should be unchanged.
    assert lateral.load_kg == 10.0
