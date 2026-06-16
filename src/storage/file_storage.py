# file_storage.py is the concrete implementation of the storage repositories.
# It persists data as JSON files on disk.
#
# All serialisation and deserialisation logic lives here.
# Nothing outside this module needs to know that storage is file-based.

import json
import os
from datetime import date
from src.models.exercise import Exercise
from src.models.exercise_prescription import ExercisePrescription
from src.models.workout_day import WorkoutDay
from src.models.program import Program
from src.models.set_result import SetResult
from src.models.exercise_result import ExerciseResult
from src.models.workout_session import WorkoutSession
from src.models.progression_decision import ProgressionDecision
from src.storage.repository import ProgramRepository, SessionRepository, DecisionRepository


# --- Serialisers ---
# Each serialiser converts a model instance to a plain dict for JSON storage.

def _serialise_exercise(exercise: Exercise) -> dict:
    return {
        "name": exercise.name,
        "exercise_type": exercise.exercise_type,
    }

def _serialise_prescription(prescription: ExercisePrescription) -> dict:
    return {
        "exercise": _serialise_exercise(prescription.exercise),
        "sets": prescription.sets,
        "rep_min": prescription.rep_min,
        "rep_max": prescription.rep_max,
        "load_kg": prescription.load_kg,
        "rir_target": prescription.rir_target,
    }

def _serialise_workout_day(day: WorkoutDay) -> dict:
    return {
        "name": day.name,
        "prescriptions": [_serialise_prescription(p) for p in day.prescriptions],
    }

def _serialise_program(program: Program) -> dict:
    return {
        "name": program.name,
        "workout_days": [_serialise_workout_day(d) for d in program.workout_days],
    }

def _serialise_set_result(set_result: SetResult) -> dict:
    return {
        "reps": set_result.reps,
        "load_kg": set_result.load_kg,
        "rpe": set_result.rpe,
    }

def _serialise_exercise_result(result: ExerciseResult) -> dict:
    return {
        "prescription": _serialise_prescription(result.prescription),
        "set_results": [_serialise_set_result(s) for s in result.set_results],
    }

def _serialise_session(session: WorkoutSession) -> dict:
    return {
        "workout_day": _serialise_workout_day(session.workout_day),
        "session_date": session.session_date.isoformat(),
        "exercise_results": [_serialise_exercise_result(r) for r in session.exercise_results],
    }

def _serialise_decision(decision: ProgressionDecision) -> dict:
    return {
        "exercise": _serialise_exercise(decision.exercise),
        "current_load_kg": decision.current_load_kg,
        "new_load_kg": decision.new_load_kg,
        "outcome": decision.outcome,
        "reason": decision.reason,
    }


# --- Deserialisers ---
# Each deserialiser reconstructs a model instance from a plain dict.

def _deserialise_exercise(data: dict) -> Exercise:
    return Exercise(
        name=data["name"],
        exercise_type=data["exercise_type"],
    )

def _deserialise_prescription(data: dict) -> ExercisePrescription:
    return ExercisePrescription(
        exercise=_deserialise_exercise(data["exercise"]),
        sets=data["sets"],
        rep_min=data["rep_min"],
        rep_max=data["rep_max"],
        load_kg=data["load_kg"],
        rir_target=data["rir_target"],
    )

def _deserialise_workout_day(data: dict) -> WorkoutDay:
    return WorkoutDay(
        name=data["name"],
        prescriptions=[_deserialise_prescription(p) for p in data["prescriptions"]],
    )

def _deserialise_program(data: dict) -> Program:
    return Program(
        name=data["name"],
        workout_days=[_deserialise_workout_day(d) for d in data["workout_days"]],
    )

def _deserialise_set_result(data: dict) -> SetResult:
    return SetResult(
        reps=data["reps"],
        load_kg=data["load_kg"],
        rpe=data["rpe"],
    )

def _deserialise_exercise_result(data: dict) -> ExerciseResult:
    return ExerciseResult(
        prescription=_deserialise_prescription(data["prescription"]),
        set_results=[_deserialise_set_result(s) for s in data["set_results"]],
    )

def _deserialise_session(data: dict) -> WorkoutSession:
    return WorkoutSession(
        workout_day=_deserialise_workout_day(data["workout_day"]),
        session_date=date.fromisoformat(data["session_date"]),
        exercise_results=[_deserialise_exercise_result(r) for r in data["exercise_results"]],
    )


# --- Concrete repository implementations ---

class FileProgramRepository(ProgramRepository):

    def __init__(self, path: str = "data/program.json"):
        # path is the file location for the programme JSON.
        # Defaults to data/program.json relative to the working directory.
        self.path = path

    def load_program(self) -> Program:
        # Raises FileNotFoundError if no programme file exists yet.
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"No programme found at {self.path}")
        with open(self.path, "r") as f:
            data = json.load(f)
        return _deserialise_program(data)

    def save_program(self, program: Program) -> None:
        # Creates the data directory if it does not already exist.
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(_serialise_program(program), f, indent=2)


class FileSessionRepository(SessionRepository):

    def __init__(self, path: str = "data/sessions.json"):
        # All sessions are stored as a JSON array in a single file.
        self.path = path

    def save_session(self, session: WorkoutSession) -> None:
        # Loads existing sessions, appends the new one, and saves back.
        sessions = self.load_sessions()
        sessions.append(session)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump([_serialise_session(s) for s in sessions], f, indent=2)

    def load_sessions(self) -> list[WorkoutSession]:
        # Returns an empty list if no sessions file exists yet.
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r") as f:
            data = json.load(f)
        return [_deserialise_session(s) for s in data]


class FileDecisionRepository(DecisionRepository):

    def __init__(self, path: str = "data/decisions.json"):
        # All decisions are stored as a JSON array in a single file.
        self.path = path

    def save_decisions(
        self,
        session_date: str,
        decisions: list[ProgressionDecision],
    ) -> None:
        # Loads existing decision records, appends the new batch, saves back.
        # Each record groups decisions by session date for easy review.
        existing = self._load_raw()
        existing.append({
            "session_date": session_date,
            "decisions": [_serialise_decision(d) for d in decisions],
        })
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(existing, f, indent=2)

    def _load_raw(self) -> list[dict]:
        # Returns raw JSON data without deserialising to model instances.
        # Decisions are append-only and never need to be reconstructed
        # as model objects - they are read for reporting only.
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r") as f:
            return json.load(f)
