# ProgramService is the interface between the rest of the application
# and programme storage. It wraps the ProgramRepository and provides
# a clean, intention-revealing API for loading and saving the programme.
#
# Keeping this as a service rather than calling the repository directly
# means the rest of the application never needs to know where or how
# the programme is stored.

from src.models.program import Program
from src.storage.repository import ProgramRepository


class ProgramService:

    def __init__(self, repository: ProgramRepository):
        # The repository is injected rather than instantiated here.
        # This means ProgramService works with any storage backend
        # that implements the ProgramRepository interface.
        self.repository = repository

    def load_program(self) -> Program:
        # Load and return the current programme from storage.
        # Raises FileNotFoundError if no programme has been saved yet.
        return self.repository.load_program()

    def save_program(self, program: Program) -> None:
        # Persist the programme to storage.
        # Called after progression decisions have been applied to
        # produce an updated programme.
        self.repository.save_program(program)

    def program_exists(self) -> bool:
        # Returns True if a programme exists in storage, False otherwise.
        # Used by main.py to detect first-run state and give a helpful
        # error message rather than a raw FileNotFoundError.
        try:
            self.repository.load_program()
            return True
        except FileNotFoundError:
            return False
