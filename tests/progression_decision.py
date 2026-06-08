# ProgressionDecision is a pure data model representing the outcome of the
# progression engine evaluating a single exercise after a session.
# It records what was decided, why, and what the load change is.
# This is progression domain data - it is the output of the engine,
# not an input to it.

from src.models.exercise import Exercise


class ProgressionDecision:

    # The set of valid decision outcomes.
    # increase: load should go up next session.
    # maintain: load stays the same next session.
    # decrease: load should come down next session.
    VALID_OUTCOMES = {"increase", "maintain", "decrease"}

    def __init__(
        self,
        exercise: Exercise,
        current_load_kg: float,
        new_load_kg: float,
        outcome: str,
        reason: str,
    ):
        # exercise is the exercise this decision applies to.
        if not isinstance(exercise, Exercise):
            raise TypeError("exercise must be an instance of Exercise")

        # current_load_kg is the load used in the session just completed.
        if current_load_kg <= 0:
            raise ValueError("current_load_kg must be greater than 0")

        # new_load_kg is the load prescribed for the next session.
        # Must be positive. Can equal current_load_kg for a maintain decision.
        if new_load_kg <= 0:
            raise ValueError("new_load_kg must be greater than 0")

        # outcome is the progression decision - one of the three valid values.
        if outcome not in self.VALID_OUTCOMES:
            raise ValueError(f"outcome must be one of {self.VALID_OUTCOMES}")

        # Enforce internal consistency between outcome and load change.
        # An increase outcome must have a higher new load,
        # a decrease outcome must have a lower new load,
        # a maintain outcome must have an unchanged load.
        if outcome == "increase" and new_load_kg <= current_load_kg:
            raise ValueError("outcome is 'increase' but new_load_kg is not greater than current_load_kg")
        if outcome == "decrease" and new_load_kg >= current_load_kg:
            raise ValueError("outcome is 'decrease' but new_load_kg is not less than current_load_kg")
        if outcome == "maintain" and new_load_kg != current_load_kg:
            raise ValueError("outcome is 'maintain' but new_load_kg differs from current_load_kg")

        # reason is a human-readable explanation of why this decision was made.
        # Required - explainability is a core purpose of this model.
        if not reason or not reason.strip():
            raise ValueError("reason cannot be empty")

        self.exercise = exercise
        self.current_load_kg = current_load_kg
        self.new_load_kg = new_load_kg
        self.outcome = outcome
        self.reason = reason

    @property
    def load_change_kg(self) -> float:
        # The absolute change in load as a result of this decision.
        # Positive for increase, negative for decrease, zero for maintain.
        return self.new_load_kg - self.current_load_kg

    def __repr__(self):
        # Readable representation showing the exercise, outcome, and load change.
        return (
            f"ProgressionDecision("
            f"exercise={self.exercise.name!r}, "
            f"outcome={self.outcome!r}, "
            f"load={self.current_load_kg}kg -> {self.new_load_kg}kg, "
            f"reason={self.reason!r})"
        )

    def __eq__(self, other):
        # Two decisions are equal if all fields match.
        if not isinstance(other, ProgressionDecision):
            return False
        return (
            self.exercise == other.exercise
            and self.current_load_kg == other.current_load_kg
            and self.new_load_kg == other.new_load_kg
            and self.outcome == other.outcome
            and self.reason == other.reason
        )
