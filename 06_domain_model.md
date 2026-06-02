# Domain Model

## Overview

The system consists of two domains:

1. Planning Domain
2. Execution Domain

Planning represents intended training.

Execution represents completed training.

---

## Planning Domain

this can be thought of as the input data to the progression engine

### Program

Represents a complete training program.

Attributes:
- id
- name
- start_date
- workout_days

Relationships:
- Contains multiple WorkoutDays

---

### WorkoutDay

Represents a single training day.

Attributes:
- name
- exercises

Relationships:
- Contains multiple ExercisePrescriptions

---

### ExercisePrescription

Represents planned exercise parameters.

Attributes:
- exercise_name
- target_sets
- rep_range_min
- rep_range_max
- target_weight

Relationships:
- References one Exercise

---

### Exercise

Represents an exercise definition.

Attributes:
- name
- muscle_group

---

## Execution Domain

### WorkoutSession

Represents a completed workout.

Attributes:
- session_date
- workout_day_name
- exercise_results

Relationships:
- Contains multiple ExerciseResults

---

### ExerciseResult

Represents performance for one exercise.

Attributes:
- exercise_name
- set_results

Relationships:
- Contains multiple SetResults

---

### SetResult

### ProgressionDecision

Represents why a load changed. this key for explainability to the user concern about over training

Attributes:
- exercise_name
- previous_weight
- new_weight
- reason
- generated_date

Represents a completed set.

Attributes:
- reps
- weight
- rpe
