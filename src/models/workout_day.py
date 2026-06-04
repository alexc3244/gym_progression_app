# WorkoutDay is a pure data model representing a single named training day
# within the programme. It holds an ordered list of exercise prescriptions.
# No progression logic, no storage concerns belong here.

from src.models.exercise_prescription import ExercisePrescription


class WorkoutDay:

    def __init__(self, name: str, prescriptions: list[ExercisePrescription]):
        # name identifies the training day, e.g. "Push A", "Pull B".
        # Must be a non-empty string.
        if not name or not name.strip():
            raise ValueError("name cannot be empty")

        # prescriptions is the ordered list of exercises for this day.
        # Must be a list and cannot be empty - a day with no exercises
        # is not a valid workout day.
        if not isinstance(prescriptions, list):
            raise TypeError("prescriptions must be a list")
        if len(prescriptions) == 0:
            raise ValueError("prescriptions cannot be empty")

        # Every item in the list must be an ExercisePrescription instance.
        for i, p in enumerate(prescriptions):
            if not isinstance(p, ExercisePrescription):
                raise TypeError(
                    f"all items in prescriptions must be ExercisePrescription instances, "
                    f"got {type(p).__name__} at index {i}"
                )

        self.name = name
        # Store a copy to prevent external mutation of the internal list.
        self.prescriptions = list(prescriptions)

    def __repr__(self):
        # Readable representation showing the day name and number of exercises.
        return (
            f"WorkoutDay(name={self.name!r}, "
            f"prescriptions={len(self.prescriptions)} exercise(s))"
        )

    def __eq__(self, other):
        # Two workout days are equal if their name and all prescriptions match.
        if not isinstance(other, WorkoutDay):
            return False
        return self.name == other.name and self.prescriptions == other.prescriptions
