# ExercisePrescription is a pure data model representing a planned exercise
# within a WorkoutDay. It holds the prescription only - no results, no logic.

from src.models.exercise import Exercise


class ExercisePrescription:

    def __init__(
        self,
        exercise: Exercise,
        sets: int,
        rep_min: int,
        rep_max: int,
        load_kg: float,
        rir_target: int,
    ):
        # The exercise being prescribed. Must be a valid Exercise instance.
        if not isinstance(exercise, Exercise):
            raise TypeError("exercise must be an instance of Exercise")

        # Sets must be a positive integer.
        if sets < 1:
            raise ValueError("sets must be at least 1")

        # rep_min and rep_max define the target rep range.
        # rep_min must be at least 1 and cannot exceed rep_max.
        if rep_min < 1:
            raise ValueError("rep_min must be at least 1")
        if rep_max < rep_min:
            raise ValueError("rep_max must be greater than or equal to rep_min")

        # load_kg is the prescribed working weight. Must be positive.
        if load_kg <= 0:
            raise ValueError("load_kg must be greater than 0")

        # rir_target is the target Reps in Reserve. Must be non-negative.
        # 0 is valid (taken to failure).
        if rir_target < 0:
            raise ValueError("rir_target must be 0 or greater")

        self.exercise = exercise
        self.sets = sets
        self.rep_min = rep_min
        self.rep_max = rep_max
        self.load_kg = load_kg
        self.rir_target = rir_target

    def __repr__(self):
        # Readable representation for debugging and logging.
        return (
            f"ExercisePrescription("
            f"exercise={self.exercise.name!r}, "
            f"sets={self.sets}, "
            f"reps={self.rep_min}-{self.rep_max}, "
            f"load_kg={self.load_kg}, "
            f"rir_target={self.rir_target})"
        )

    def __eq__(self, other):
        # Two prescriptions are equal if all fields match.
        if not isinstance(other, ExercisePrescription):
            return False
        return (
            self.exercise == other.exercise
            and self.sets == other.sets
            and self.rep_min == other.rep_min
            and self.rep_max == other.rep_max
            and self.load_kg == other.load_kg
            and self.rir_target == other.rir_target
        )
