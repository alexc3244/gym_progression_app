# main.py is the CLI entry point for the hypertrophy engine.
# It wires together the services and storage layer into a runnable application.
#
# Commands:
#   python main.py show-program         → print the current programme and loads
#   python main.py log-session          → interactively log a completed session
#   python main.py show-decisions       → print the progression decision history
#
# All business logic lives in the engine and services.
# main.py only handles user input, output, and orchestration.

import sys
import json
from datetime import date

from src.models.exercise import Exercise
from src.models.exercise_prescription import ExercisePrescription
from src.models.set_result import SetResult
from src.models.exercise_result import ExerciseResult
from src.models.workout_day import WorkoutDay
from src.models.workout_session import WorkoutSession

from src.services.program_service import ProgramService
from src.services.session_service import SessionService
from src.storage.file_storage import (
    FileProgramRepository,
    FileSessionRepository,
    FileDecisionRepository,
)


# --- Dependency setup ---
# All concrete dependencies are wired here at the top level.
# Services receive their dependencies via injection - they never
# instantiate storage directly.

program_repo = FileProgramRepository(path="data/program.json")
session_repo = FileSessionRepository(path="data/sessions.json")
decision_repo = FileDecisionRepository(path="data/decisions.json")

program_service = ProgramService(repository=program_repo)
session_service = SessionService()


# --- Output helpers ---

def print_divider():
    print("-" * 50)

def print_program(program):
    # Prints the current programme with all exercises and their current loads.
    print(f"\nProgramme: {program.name}")
    for day in program.workout_days:
        print_divider()
        print(f"  {day.name}")
        for p in day.prescriptions:
            print(
                f"    {p.exercise.name} ({p.exercise.exercise_type})"
                f"  |  {p.sets} x {p.rep_min}-{p.rep_max} reps"
                f"  |  {p.load_kg}kg"
                f"  |  RIR {p.rir_target}"
            )
    print_divider()


# --- Commands ---

def cmd_show_program():
    # Loads and prints the current programme.
    if not program_service.program_exists():
        print("\nNo programme found. Add a programme to data/program.json to get started.")
        return

    program = program_service.load_program()
    print_program(program)


def cmd_log_session():
    # Interactively logs a completed session, runs progression,
    # prints decisions, and saves the updated programme.

    if not program_service.program_exists():
        print("\nNo programme found. Add a programme to data/program.json first.")
        return

    program = program_service.load_program()

    # Step 1 — select the workout day.
    print("\nWhich day did you train?")
    for i, day in enumerate(program.workout_days):
        print(f"  {i + 1}. {day.name}")

    day_index = _prompt_int("Enter number: ", min_val=1, max_val=len(program.workout_days)) - 1
    selected_day = program.workout_days[day_index]

    # Step 2 — log each exercise in the day.
    exercise_results = []

    for prescription in selected_day.prescriptions:
        print(f"\n  {prescription.exercise.name}")
        print(
            f"  Prescribed: {prescription.sets} x "
            f"{prescription.rep_min}-{prescription.rep_max} reps "
            f"@ {prescription.load_kg}kg  RIR {prescription.rir_target}"
        )

        set_results = []
        for set_num in range(1, prescription.sets + 1):
            print(f"    Set {set_num}:")
            reps = _prompt_int("      Reps completed: ", min_val=1)
            load = _prompt_float("      Load (kg): ", min_val=0.01)
            rpe = _prompt_float("      RPE (1.0 - 10.0): ", min_val=1.0, max_val=10.0)
            set_results.append(SetResult(reps=reps, load_kg=load, rpe=rpe))

        exercise_results.append(
            ExerciseResult(prescription=prescription, set_results=set_results)
        )

    # Step 3 — build the session.
    session = WorkoutSession(
        workout_day=selected_day,
        session_date=date.today(),
        exercise_results=exercise_results,
    )

    # Step 4 — run progression engine via session service.
    decisions, updated_program = session_service.process_session(session, program)

    # Step 5 — print decisions.
    print("\nProgression decisions:")
    print_divider()
    for decision in decisions:
        arrow = "→"
        print(
            f"  {decision.exercise.name}: "
            f"{decision.current_load_kg}kg {arrow} {decision.new_load_kg}kg "
            f"[{decision.outcome.upper()}]"
        )
        print(f"    {decision.reason}")
    print_divider()

    # Step 6 — persist session, decisions, and updated programme.
    session_repo.save_session(session)
    decision_repo.save_decisions(str(date.today()), decisions)
    program_service.save_program(updated_program)

    print("\nSession logged. Programme updated.")


def cmd_show_decisions():
    # Prints the full progression decision history from storage.
    if not os.path.exists("data/decisions.json"):
        print("\nNo decisions logged yet.")
        return

    with open("data/decisions.json") as f:
        data = json.load(f)

    if not data:
        print("\nNo decisions logged yet.")
        return

    print("\nProgression history:")
    for record in data:
        print_divider()
        print(f"  Session: {record['session_date']}")
        for d in record["decisions"]:
            print(
                f"    {d['exercise']['name']}: "
                f"{d['current_load_kg']}kg → {d['new_load_kg']}kg "
                f"[{d['outcome'].upper()}]"
            )
            print(f"      {d['reason']}")
    print_divider()


# --- Input helpers ---

def _prompt_int(prompt: str, min_val: int = None, max_val: int = None) -> int:
    # Prompts the user for an integer, re-prompting on invalid input.
    while True:
        try:
            value = int(input(prompt))
            if min_val is not None and value < min_val:
                print(f"      Must be at least {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"      Must be at most {max_val}.")
                continue
            return value
        except ValueError:
            print("      Please enter a whole number.")


def _prompt_float(prompt: str, min_val: float = None, max_val: float = None) -> float:
    # Prompts the user for a float, re-prompting on invalid input.
    while True:
        try:
            value = float(input(prompt))
            if min_val is not None and value < min_val:
                print(f"      Must be at least {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"      Must be at most {max_val}.")
                continue
            return value
        except ValueError:
            print("      Please enter a number.")


# --- Entry point ---

COMMANDS = {
    "show-program": cmd_show_program,
    "log-session": cmd_log_session,
    "show-decisions": cmd_show_decisions,
}

if __name__ == "__main__":
    import os

    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("\nUsage: python main.py <command>")
        print("Commands:")
        for name in COMMANDS:
            print(f"  {name}")
        sys.exit(1)

    COMMANDS[sys.argv[1]]()
