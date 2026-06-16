# SessionService orchestrates the workflow around a workout session.
# It sits between the engine and storage - it does not contain progression
# logic (that belongs in the engine) and does not handle persistence directly
# (that belongs in storage).
#
# Responsibilities:
# - Accept a completed WorkoutSession
# - Run the progression engine against it
# - Return the resulting ProgressionDecisions
# - Apply those decisions to produce an updated Program
#
# This service is stateless. It receives everything it needs as arguments
# and returns results - no internal state is stored on the instance.

from src.models.workout_session import WorkoutSession
from src.models.program import Program
from src.models.exercise_prescription import ExercisePrescription
from src.models.workout_day import WorkoutDay
from src.models.progression_decision import ProgressionDecision
from src.engine.progression import evaluate_session


class SessionService:

    def process_session(
        self,
        session: WorkoutSession,
        program: Program,
    ) -> tuple[list[ProgressionDecision], Program]:
        # The main entry point for processing a completed session.
        # Returns a tuple of:
        # - The list of ProgressionDecisions produced by the engine
        # - An updated Program with new loads applied
        #
        # The original Program is not mutated. A new Program is returned.

        # Run the progression engine to get decisions.
        decisions = evaluate_session(session, program)

        # Apply decisions to produce an updated programme.
        updated_program = self._apply_decisions(program, decisions)

        return decisions, updated_program

    def _apply_decisions(
        self,
        program: Program,
        decisions: list[ProgressionDecision],
    ) -> Program:
        # Applies a list of ProgressionDecisions to the programme and returns
        # a new Program with updated loads.
        #
        # The original Program is not mutated - new model instances are
        # constructed throughout. This keeps the original state intact for
        # logging and comparison.

        # Build a lookup from exercise name to new load for O(1) access.
        load_updates = {
            decision.exercise.name: decision.new_load_kg
            for decision in decisions
        }

        # Rebuild the programme with updated prescriptions where applicable.
        updated_days = [
            self._update_workout_day(day, load_updates)
            for day in program.workout_days
        ]

        return Program(name=program.name, workout_days=updated_days)

    def _update_workout_day(
        self,
        day: WorkoutDay,
        load_updates: dict[str, float],
    ) -> WorkoutDay:
        # Rebuilds a WorkoutDay with updated loads applied to any prescriptions
        # whose exercise appears in the load_updates dictionary.
        #
        # Prescriptions for exercises not in load_updates are carried over
        # unchanged - this handles the case where a session only covers a
        # subset of exercises in the programme.

        updated_prescriptions = [
            self._update_prescription(prescription, load_updates)
            for prescription in day.prescriptions
        ]

        return WorkoutDay(name=day.name, prescriptions=updated_prescriptions)

    def _update_prescription(
        self,
        prescription: ExercisePrescription,
        load_updates: dict[str, float],
    ) -> ExercisePrescription:
        # Returns an updated ExercisePrescription if the exercise has a new load,
        # or the original prescription unchanged if it does not.

        exercise_name = prescription.exercise.name

        if exercise_name not in load_updates:
            # No decision was made for this exercise - carry over unchanged.
            return prescription

        new_load = load_updates[exercise_name]

        # Construct a new prescription with the updated load.
        # All other fields (sets, rep range, RIR target) are unchanged.
        return ExercisePrescription(
            exercise=prescription.exercise,
            sets=prescription.sets,
            rep_min=prescription.rep_min,
            rep_max=prescription.rep_max,
            load_kg=new_load,
            rir_target=prescription.rir_target,
        )
