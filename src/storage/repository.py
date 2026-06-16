# repository.py defines the abstract storage interface.
# The rest of the codebase depends on this interface only.
# The concrete implementation (file_storage.py) is the only place
# that knows how data is actually persisted.
#
# This pattern means swapping storage backends (file → database, etc.)
# requires changing only the concrete implementation, not the services
# or engine that use it.

from abc import ABC, abstractmethod
from src.models.program import Program
from src.models.workout_session import WorkoutSession
from src.models.progression_decision import ProgressionDecision


class ProgramRepository(ABC):

    @abstractmethod
    def load_program(self) -> Program:
        # Load and return the current programme from storage.
        # Raises FileNotFoundError if no programme exists yet.
        pass

    @abstractmethod
    def save_program(self, program: Program) -> None:
        # Persist the programme to storage.
        # Overwrites any existing programme.
        pass


class SessionRepository(ABC):

    @abstractmethod
    def save_session(self, session: WorkoutSession) -> None:
        # Persist a completed workout session to storage.
        pass

    @abstractmethod
    def load_sessions(self) -> list[WorkoutSession]:
        # Load and return all previously saved sessions.
        # Returns an empty list if no sessions exist yet.
        pass


class DecisionRepository(ABC):

    @abstractmethod
    def save_decisions(
        self,
        session_date: str,
        decisions: list[ProgressionDecision],
    ) -> None:
        # Persist the progression decisions from a session to storage.
        # session_date is used as a key to group decisions by session.
        pass
