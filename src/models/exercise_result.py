# ExerciseResult is a pure data model representing the logged outcome
# of a single exercise within a workout session.
# It links a prescription (the plan) to the actual set results (what happened).
# This is execution domain data, not planning domain data.

from src.models.exercise_prescription import ExercisePrescription
from src.models.set_result import SetResult


class ExerciseResult:

    def __init__(self, prescription: ExercisePrescription, set_results: list[SetResult]):
        # prescription is the planned exercise this result is logged against.
        # Linking result to prescription is what allows the progression engine
        # to compare planned vs actual performance.
        if not isinstance(prescription, ExercisePrescription):
            raise TypeError("prescription must be an instance of ExercisePrescription")

        # set_results is the ordered list of sets performed for this exercise.
        # Must be a list and cannot be empty - an exercise with no sets
        # recorded was not performed.
        if not isinstance(set_results, list):
            raise TypeError("set_results must be a list")
        if len(set_results) == 0:
            raise ValueError("set_results cannot be empty")

        # Every item in the list must be a SetResult instance.
        for i, s in enumerate(set_results):
            if not isinstance(s, SetResult):
                raise TypeError(
                    f"all items in set_results must be SetResult instances, "
                    f"got {type(s).__name__} at index {i}"
                )

        self.prescription = prescription
        # Store a copy to prevent external mutation of the internal list.
        self.set_results = list(set_results)

    @property
    def total_sets_performed(self) -> int:
        # The number of sets actually completed for this exercise.
        # Useful for comparing against the prescribed set count.
        return len(self.set_results)

    @property
    def average_rpe(self) -> float:
        # The mean RPE across all sets performed.
        # Used by the autoregulation engine to assess session difficulty.
        return sum(s.rpe for s in self.set_results) / len(self.set_results)

    @property
    def average_reps(self) -> float:
        # The mean reps across all sets performed.
        # Used by the progression engine to assess whether the rep target was met.
        return sum(s.reps for s in self.set_results) / len(self.set_results)

    def __repr__(self):
        # Readable representation showing exercise name and sets completed.
        return (
            f"ExerciseResult("
            f"exercise={self.prescription.exercise.name!r}, "
            f"sets_performed={self.total_sets_performed}, "
            f"avg_rpe={self.average_rpe:.1f})"
        )

    def __eq__(self, other):
        # Two exercise results are equal if their prescription and
        # all set results match.
        if not isinstance(other, ExerciseResult):
            return False
        return (
            self.prescription == other.prescription
            and self.set_results == other.set_results
        )
