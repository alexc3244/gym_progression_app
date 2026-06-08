# WorkoutSession is a pure data model representing a completed training session.
# It is the top-level execution domain model - the execution counterpart
# to WorkoutDay in the planning domain.
# No progression logic, no storage concerns belong here.

from datetime import date
from src.models.workout_day import WorkoutDay
from src.models.exercise_result import ExerciseResult


class WorkoutSession:

    def __init__(
        self,
        workout_day: WorkoutDay,
        session_date: date,
        exercise_results: list[ExerciseResult],
    ):
        # workout_day is the planned day this session was performed against.
        # Links execution back to the planning domain, allowing the progression
        # engine to compare what was planned vs what was performed.
        if not isinstance(workout_day, WorkoutDay):
            raise TypeError("workout_day must be an instance of WorkoutDay")

        # session_date is the calendar date the session was performed.
        # Used for ordering sessions chronologically during progression evaluation.
        if not isinstance(session_date, date):
            raise TypeError("session_date must be a datetime.date instance")

        # exercise_results is the ordered list of exercise outcomes for this session.
        # Must be a list and cannot be empty - a session with no exercises
        # logged was not a valid session.
        if not isinstance(exercise_results, list):
            raise TypeError("exercise_results must be a list")
        if len(exercise_results) == 0:
            raise ValueError("exercise_results cannot be empty")

        # Every item in the list must be an ExerciseResult instance.
        for i, r in enumerate(exercise_results):
            if not isinstance(r, ExerciseResult):
                raise TypeError(
                    f"all items in exercise_results must be ExerciseResult instances, "
                    f"got {type(r).__name__} at index {i}"
                )

        self.workout_day = workout_day
        self.session_date = session_date
        # Store a copy to prevent external mutation of the internal list.
        self.exercise_results = list(exercise_results)

    @property
    def total_exercises(self) -> int:
        # The number of exercises logged in this session.
        return len(self.exercise_results)

    @property
    def average_session_rpe(self) -> float:
        # The mean RPE across all exercises in the session.
        # Gives a high-level signal of overall session difficulty
        # for use by the autoregulation engine.
        return sum(r.average_rpe for r in self.exercise_results) / len(self.exercise_results)

    def get_result_for_exercise(self, exercise_name: str) -> ExerciseResult:
        # Retrieve the ExerciseResult for a given exercise name.
        # Used by the progression engine to look up performance on a
        # specific exercise after a session is logged.
        # Raises ValueError if no result for that exercise exists.
        for result in self.exercise_results:
            if result.prescription.exercise.name == exercise_name:
                return result
        raise ValueError(f"no ExerciseResult found for exercise {exercise_name!r}")

    def __repr__(self):
        # Readable representation showing the day name, date, and exercise count.
        return (
            f"WorkoutSession("
            f"workout_day={self.workout_day.name!r}, "
            f"session_date={self.session_date}, "
            f"total_exercises={self.total_exercises})"
        )

    def __eq__(self, other):
        # Two sessions are equal if their workout day, date, and all
        # exercise results match.
        if not isinstance(other, WorkoutSession):
            return False
        return (
            self.workout_day == other.workout_day
            and self.session_date == other.session_date
            and self.exercise_results == other.exercise_results
        )
