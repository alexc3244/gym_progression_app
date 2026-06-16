import pytest
import os
import json
from datetime import date
from src.models.exercise import Exercise
from src.models.exercise_prescription import ExercisePrescription
from src.models.set_result import SetResult
from src.models.exercise_result import ExerciseResult
from src.models.workout_day import WorkoutDay
from src.models.workout_session import WorkoutSession
from src.models.program import Program
from src.models.progression_decision import ProgressionDecision
from src.storage.file_storage import (
    FileProgramRepository,
    FileSessionRepository,
    FileDecisionRepository,
)


# --- Helpers ---

@pytest.fixture
def tmp_path_str(tmp_path):
    # pytest's tmp_path fixture provides a temporary directory.
    # We use it to avoid writing real files during tests.
    return str(tmp_path)

@pytest.fixture
def prescription():
    exercise = Exercise(name="Bench Press", exercise_type="compound")
    return ExercisePrescription(
        exercise=exercise,
        sets=3,
        rep_min=8,
        rep_max=12,
        load_kg=80.0,
        rir_target=2,
    )

@pytest.fixture
def program(prescription):
    day = WorkoutDay(name="Push A", prescriptions=[prescription])
    return Program(name="PPL Block 1", workout_days=[day])

@pytest.fixture
def session(prescription):
    set_results = [
        SetResult(reps=10, load_kg=80.0, rpe=8.0),
        SetResult(reps=9, load_kg=80.0, rpe=8.5),
    ]
    exercise_result = ExerciseResult(
        prescription=prescription,
        set_results=set_results,
    )
    day = WorkoutDay(name="Push A", prescriptions=[prescription])
    return WorkoutSession(
        workout_day=day,
        session_date=date(2026, 6, 16),
        exercise_results=[exercise_result],
    )

@pytest.fixture
def decision():
    exercise = Exercise(name="Bench Press", exercise_type="compound")
    return ProgressionDecision(
        exercise=exercise,
        current_load_kg=80.0,
        new_load_kg=82.5,
        outcome="increase",
        reason="Top of rep range achieved at optimal RPE.",
    )


# --- FileProgramRepository ---

def test_save_and_load_program(tmp_path_str, program):
    # A saved programme should be recoverable as an equal object.
    repo = FileProgramRepository(path=os.path.join(tmp_path_str, "program.json"))
    repo.save_program(program)
    loaded = repo.load_program()
    assert loaded == program

def test_load_program_raises_when_no_file(tmp_path_str):
    # Loading before saving should raise FileNotFoundError.
    repo = FileProgramRepository(path=os.path.join(tmp_path_str, "program.json"))
    with pytest.raises(FileNotFoundError):
        repo.load_program()

def test_save_program_overwrites_existing(tmp_path_str, program, prescription):
    # Saving a second programme should overwrite the first.
    repo = FileProgramRepository(path=os.path.join(tmp_path_str, "program.json"))
    repo.save_program(program)

    updated_exercise = Exercise(name="Bench Press", exercise_type="compound")
    updated_prescription = ExercisePrescription(
        exercise=updated_exercise,
        sets=3,
        rep_min=8,
        rep_max=12,
        load_kg=82.5,
        rir_target=2,
    )
    updated_day = WorkoutDay(name="Push A", prescriptions=[updated_prescription])
    updated_program = Program(name="PPL Block 1", workout_days=[updated_day])

    repo.save_program(updated_program)
    loaded = repo.load_program()

    assert loaded.get_day("Push A").prescriptions[0].load_kg == 82.5


# --- FileSessionRepository ---

def test_save_and_load_session(tmp_path_str, session):
    # A saved session should be recoverable as an equal object.
    repo = FileSessionRepository(path=os.path.join(tmp_path_str, "sessions.json"))
    repo.save_session(session)
    loaded = repo.load_sessions()
    assert len(loaded) == 1
    assert loaded[0] == session

def test_load_sessions_returns_empty_list_when_no_file(tmp_path_str):
    # Loading before saving should return an empty list, not raise.
    repo = FileSessionRepository(path=os.path.join(tmp_path_str, "sessions.json"))
    assert repo.load_sessions() == []

def test_multiple_sessions_accumulate(tmp_path_str, session):
    # Saving twice should result in two sessions on load.
    repo = FileSessionRepository(path=os.path.join(tmp_path_str, "sessions.json"))
    repo.save_session(session)
    repo.save_session(session)
    loaded = repo.load_sessions()
    assert len(loaded) == 2


# --- FileDecisionRepository ---

def test_save_and_load_decisions(tmp_path_str, decision):
    # Saved decisions should be persisted and readable from raw JSON.
    repo = FileDecisionRepository(path=os.path.join(tmp_path_str, "decisions.json"))
    repo.save_decisions("2026-06-16", [decision])

    with open(os.path.join(tmp_path_str, "decisions.json")) as f:
        data = json.load(f)

    assert len(data) == 1
    assert data[0]["session_date"] == "2026-06-16"
    assert data[0]["decisions"][0]["outcome"] == "increase"

def test_decisions_accumulate_across_sessions(tmp_path_str, decision):
    # Decisions from multiple sessions should all be stored.
    repo = FileDecisionRepository(path=os.path.join(tmp_path_str, "decisions.json"))
    repo.save_decisions("2026-06-16", [decision])
    repo.save_decisions("2026-06-18", [decision])

    with open(os.path.join(tmp_path_str, "decisions.json")) as f:
        data = json.load(f)

    assert len(data) == 2
