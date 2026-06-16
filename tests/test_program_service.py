import pytest
from src.models.exercise import Exercise
from src.models.exercise_prescription import ExercisePrescription
from src.models.workout_day import WorkoutDay
from src.models.program import Program
from src.services.program_service import ProgramService


# --- Helpers ---

class InMemoryProgramRepository:
    # A lightweight in-memory repository used for testing only.
    # Avoids any file system dependency in service-level tests.

    def __init__(self):
        self._program = None

    def load_program(self) -> Program:
        if self._program is None:
            raise FileNotFoundError("No programme in memory")
        return self._program

    def save_program(self, program: Program) -> None:
        self._program = program


@pytest.fixture
def repository():
    return InMemoryProgramRepository()

@pytest.fixture
def service(repository):
    return ProgramService(repository=repository)

@pytest.fixture
def program():
    exercise = Exercise(name="Bench Press", exercise_type="compound")
    prescription = ExercisePrescription(
        exercise=exercise,
        sets=3,
        rep_min=8,
        rep_max=12,
        load_kg=80.0,
        rir_target=2,
    )
    day = WorkoutDay(name="Push A", prescriptions=[prescription])
    return Program(name="PPL Block 1", workout_days=[day])


# --- load_program ---

def test_load_program_returns_saved_program(service, repository, program):
    # A programme saved to the repository should be returned by load_program.
    repository.save_program(program)
    loaded = service.load_program()
    assert loaded == program

def test_load_program_raises_when_none_exists(service):
    # Loading before saving should raise FileNotFoundError.
    with pytest.raises(FileNotFoundError):
        service.load_program()


# --- save_program ---

def test_save_program_persists_to_repository(service, repository, program):
    # Saving via the service should make the programme available in storage.
    service.save_program(program)
    assert repository.load_program() == program


# --- program_exists ---

def test_program_exists_returns_false_when_none_saved(service):
    # Before any programme is saved, program_exists should return False.
    assert service.program_exists() is False

def test_program_exists_returns_true_after_save(service, program):
    # After saving, program_exists should return True.
    service.save_program(program)
    assert service.program_exists() is True
