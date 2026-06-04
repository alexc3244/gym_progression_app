# Exercise is a pure data model - it holds exercise metadata only.
# No progression logic, no storage concerns belong here.

class Exercise:
    # The only valid classifications for exercise_type.
    # Kept as a class-level set so the progression engine can
    # branch on type without inspecting exercise names directly.
    VALID_TYPES = {"compound", "isolation"}

    def __init__(self, name: str, exercise_type: str):
        # name is the unique identifier for an exercise within the programme.
        # An empty name would make logging and progression lookups ambiguous.
        if not name or not name.strip():
            raise ValueError("name cannot be empty")

        # exercise_type must be one of the two permitted values.
        # This enforces the controlled vocabulary defined in ADR-006
        if exercise_type not in self.VALID_TYPES:
            raise ValueError(f"exercise_type must be one of {self.VALID_TYPES}")

        self.name = name
        self.exercise_type = exercise_type

    def __repr__(self):
        # Readable representation useful for debugging and logging.
        return f"Exercise(name={self.name!r}, exercise_type={self.exercise_type!r})"

    def __eq__(self, other):
        # Two exercises are equal if both fields match.
        # Required for reliable comparison in tests and progression logic.
        if not isinstance(other, Exercise):
            return False
        return self.name == other.name and self.exercise_type == other.exercise_type
