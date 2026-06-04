# Program is the top-level planning model. It represents the full programme
# template as defined by the user. It holds an ordered list of WorkoutDays.
# No progression logic, no storage concerns belong here.

from src.models.workout_day import WorkoutDay


class Program:

    def __init__(self, name: str, workout_days: list[WorkoutDay]):
        # name identifies the programme, e.g. "PPL Hypertrophy Block 1".
        # Must be a non-empty string.
        if not name or not name.strip():
            raise ValueError("name cannot be empty")

        # workout_days is the ordered list of training days in the programme.
        # Must be a list and cannot be empty - a programme with no days
        # is not a valid programme.
        if not isinstance(workout_days, list):
            raise TypeError("workout_days must be a list")
        if len(workout_days) == 0:
            raise ValueError("workout_days cannot be empty")

        # Every item in the list must be a WorkoutDay instance.
        for i, day in enumerate(workout_days):
            if not isinstance(day, WorkoutDay):
                raise TypeError(
                    f"all items in workout_days must be WorkoutDay instances, "
                    f"got {type(day).__name__} at index {i}"
                )

        self.name = name
        # Store a copy to prevent external mutation of the internal list.
        self.workout_days = list(workout_days)

    def get_day(self, name: str) -> WorkoutDay:
        # Retrieve a WorkoutDay by name. Useful for the progression engine
        # when looking up a specific day to apply updates to.
        # Raises ValueError if no day with that name exists.
        for day in self.workout_days:
            if day.name == name:
                return day
        raise ValueError(f"no WorkoutDay named {name!r} found in programme")

    def __repr__(self):
        # Readable representation showing the programme name and day count.
        return (
            f"Program(name={self.name!r}, "
            f"workout_days={len(self.workout_days)} day(s))"
        )

    def __eq__(self, other):
        # Two programmes are equal if their name and all workout days match.
        if not isinstance(other, Program):
            return False
        return self.name == other.name and self.workout_days == other.workout_days
