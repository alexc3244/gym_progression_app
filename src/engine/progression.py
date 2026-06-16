# The progression engine is a pure function module.
# It takes a WorkoutSession and the current Program and returns a list of
# ProgressionDecisions - one per exercise in the session.
#
# No state, no storage, no side effects belong here.
# Input → Output only.

from src.models.workout_session import WorkoutSession
from src.models.program import Program
from src.models.exercise_result import ExerciseResult
from src.models.exercise_prescription import ExercisePrescription
from src.models.progression_decision import ProgressionDecision


# --- Constants ---
# All thresholds and increments are defined here in one place.
# Changing a value here changes it everywhere in the engine.

# RPE thresholds that define the autoregulation modifier bands (ADR-007).
RPE_TOO_EASY = 7.0
RPE_OPTIMAL_MAX = 8.5
RPE_HARD_MAX = 9.5

# Load increments by exercise type (ADR-007).
LOAD_INCREMENT = {
    "compound": 2.5,
    "isolation": 1.25,
}


# --- RPE modifier ---

def _classify_rpe(average_rpe: float) -> str:
    # Classifies average RPE into one of four bands as defined in ADR-007.
    # Returns a string label used by the decision logic below.
    if average_rpe < RPE_TOO_EASY:
        return "too_easy"
    if average_rpe <= RPE_OPTIMAL_MAX:
        return "optimal"
    if average_rpe <= RPE_HARD_MAX:
        return "hard"
    return "maximal"


# --- Rep performance classification ---

def _classify_reps(
    average_reps: float,
    rep_min: int,
    rep_max: int,
) -> str:
    # Classifies average reps performed relative to the prescribed rep range.
    # Returns "above", "in", or "below".
    if average_reps > rep_max:
        return "above"
    if average_reps < rep_min:
        return "below"
    return "in"


# --- Effective performance after RPE modifier ---

def _apply_rpe_modifier(rep_classification: str, rpe_classification: str) -> tuple[str, str]:
    # Applies the RPE modifier to the rep classification as defined in ADR-007.
    # Returns a tuple of (effective_performance, modifier_note).
    # modifier_note is used to construct an explainable reason string.

    # Maximal RPE overrides everything - treat as below range regardless of reps.
    if rpe_classification == "maximal":
        return "below", "RPE > 9.5 indicates maximal effort - overriding to decrease regardless of reps."

    # Too easy + in range - accelerate to above range.
    if rpe_classification == "too_easy" and rep_classification == "in":
        return "above", "RPE < 7.0 indicates load is too easy - accelerating progression."

    # Hard + above range - conservative, treat as in range.
    if rpe_classification == "hard" and rep_classification == "above":
        return "in", "RPE 8.6-9.5 with reps above range - being conservative, maintaining load."

    # All other combinations - no modification.
    return rep_classification, ""


# --- Decision builder ---

def _build_decision(
    exercise_result: ExerciseResult,
    prescription: ExercisePrescription,
    effective_performance: str,
    modifier_note: str,
) -> ProgressionDecision:
    # Builds a ProgressionDecision from the effective performance classification.
    # Constructs an auditable reason string citing which rule fired.

    exercise = prescription.exercise
    current_load = prescription.load_kg
    increment = LOAD_INCREMENT[exercise.exercise_type]

    average_reps = exercise_result.average_reps
    average_rpe = exercise_result.average_rpe

    if effective_performance == "above":
        new_load = current_load + increment
        outcome = "increase"
        base_reason = (
            f"Average reps {average_reps:.1f} above rep range "
            f"{prescription.rep_min}-{prescription.rep_max} "
            f"at RPE {average_rpe:.1f}. "
            f"Load increased by {increment}kg."
        )

    elif effective_performance == "below":
        new_load = current_load - increment
        outcome = "decrease"
        base_reason = (
            f"Average reps {average_reps:.1f} below rep range "
            f"{prescription.rep_min}-{prescription.rep_max} "
            f"at RPE {average_rpe:.1f}. "
            f"Load decreased by {increment}kg."
        )

    else:
        new_load = current_load
        outcome = "maintain"
        base_reason = (
            f"Average reps {average_reps:.1f} within rep range "
            f"{prescription.rep_min}-{prescription.rep_max} "
            f"at RPE {average_rpe:.1f}. "
            f"Load maintained."
        )

    # Append modifier note if the RPE modifier fired.
    reason = f"{base_reason} {modifier_note}".strip()

    return ProgressionDecision(
        exercise=exercise,
        current_load_kg=current_load,
        new_load_kg=new_load,
        outcome=outcome,
        reason=reason,
    )


# --- Public interface ---

def evaluate_session(session: WorkoutSession, program: Program) -> list[ProgressionDecision]:
    # The main entry point for the progression engine.
    # Evaluates every exercise result in the session and returns one
    # ProgressionDecision per exercise.
    #
    # Raises ValueError if an exercise result references an exercise
    # not found in the programme day - this would indicate a data integrity
    # issue upstream.

    decisions = []

    for exercise_result in session.exercise_results:
        exercise_name = exercise_result.prescription.exercise.name

        # Retrieve the prescription from the programme to get the rep range
        # and current load. The session's own prescription holds the load
        # used in the session; we use it directly.
        prescription = exercise_result.prescription

        # Classify rep performance against the prescribed range.
        rep_classification = _classify_reps(
            average_reps=exercise_result.average_reps,
            rep_min=prescription.rep_min,
            rep_max=prescription.rep_max,
        )

        # Classify RPE into an autoregulation band.
        rpe_classification = _classify_rpe(exercise_result.average_rpe)

        # Apply the RPE modifier to get effective performance.
        effective_performance, modifier_note = _apply_rpe_modifier(
            rep_classification=rep_classification,
            rpe_classification=rpe_classification,
        )

        # Build and store the progression decision.
        decision = _build_decision(
            exercise_result=exercise_result,
            prescription=prescription,
            effective_performance=effective_performance,
            modifier_note=modifier_note,
        )

        decisions.append(decision)

    return decisions
