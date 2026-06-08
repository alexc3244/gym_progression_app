# SetResult is a pure data model representing a single completed set.
# It records what actually happened - reps, load, and RPE.
# This is execution domain data, not planning domain data.

class SetResult:

    def __init__(self, reps: int, load_kg: float, rpe: float):
        # reps is the number of repetitions completed in this set.
        # Must be at least 1 - a set with no reps was not performed.
        if reps < 1:
            raise ValueError("reps must be at least 1")

        # load_kg is the weight used for this set. Must be positive.
        if load_kg <= 0:
            raise ValueError("load_kg must be greater than 0")

        # rpe is the Rate of Perceived Exertion on the 1-10 Borg scale.
        # Valid range is 1.0 to 10.0. Half-point increments are common
        # in practice (e.g. 7.5, 8.5) so float is used rather than int.
        if not (1.0 <= rpe <= 10.0):
            raise ValueError("rpe must be between 1.0 and 10.0 inclusive")

        self.reps = reps
        self.load_kg = load_kg
        self.rpe = rpe

    @property
    def rir(self) -> float:
        # RIR (Reps in Reserve) is derived from RPE: RIR = 10 - RPE.
        # Stored as a property rather than a field because it is always
        # derivable from RPE - there is no need to store both.
        return 10.0 - self.rpe

    def __repr__(self):
        # Readable representation for debugging and logging.
        return (
            f"SetResult(reps={self.reps}, "
            f"load_kg={self.load_kg}, "
            f"rpe={self.rpe}, "
            f"rir={self.rir})"
        )

    def __eq__(self, other):
        # Two set results are equal if all three recorded fields match.
        if not isinstance(other, SetResult):
            return False
        return (
            self.reps == other.reps
            and self.load_kg == other.load_kg
            and self.rpe == other.rpe
        )
