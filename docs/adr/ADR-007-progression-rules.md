# ADR-007: Progression rules for the hybrid progression engine

- **Status:** Accepted
- **Date:** 2026-06-16
- **Related:** ADR-006, 04_progression_logic.md

---

## Context

The progression engine must evaluate a completed WorkoutSession and produce
a ProgressionDecision for each exercise. The system uses hybrid progression,
combining deterministic rep-range rules with autoregulation signals from RPE
and RIR (ADR accepted at project outset).

The engine needs a concrete, unambiguous ruleset before implementation begins.
The rules must:

- Be implementable without external data beyond what the models already hold
- Produce a clear outcome: increase, maintain, or decrease
- Differentiate between compound and isolation exercises
- Incorporate RPE/RIR as a modulating signal, not the primary driver

---

## Decision

Progression is evaluated per exercise using the following rules, applied
in order. The first matching rule determines the outcome.

### Step 1 — Determine rep performance

Compare average reps performed (from ExerciseResult.average_reps) against
the prescribed rep range (from ExercisePrescription).

- **Above range:** average reps > rep_max
- **In range:** rep_min <= average reps <= rep_max
- **Below range:** average reps < rep_min

### Step 2 — Apply RPE modifier

Average session RPE for the exercise (ExerciseResult.average_rpe) modulates
the decision as follows:

| RPE range     | Signal         | Effect                          |
|---------------|----------------|---------------------------------|
| < 7.0         | Too easy       | Accelerate: treat as above range if in range |
| 7.0 – 8.5     | Optimal        | No modification                 |
| 8.6 – 9.5     | Hard           | Conservative: treat as in range if above range |
| > 9.5         | Maximal effort | Treat as below range regardless of reps |

### Step 3 — Determine load change

After applying the RPE modifier, the final outcome and load increment are:

| Effective performance | Outcome  | Compound increment | Isolation increment |
|-----------------------|----------|--------------------|---------------------|
| Above range           | increase | +2.5 kg            | +1.25 kg            |
| In range              | maintain | 0 kg               | 0 kg                |
| Below range           | decrease | -2.5 kg            | -1.25 kg            |

Load increments for compounds are larger because compound movements involve
greater absolute loads and respond to coarser load jumps. Isolation increments
are smaller to reflect the finer load sensitivity of single-joint movements.

---

## Rationale

**Rep range as the primary driver** is consistent with the uploaded programme,
which defines explicit rep ranges and prescribes progression based on hitting
the top of that range. This is standard double-progression methodology.

**RPE as a modifier, not the primary driver**, avoids over-reliance on a
subjective signal. RPE perception drifts across training blocks and between
sessions. Using it to modulate rather than determine progression keeps the
system robust to noise while still incorporating autoregulation.

**The RPE thresholds** (7.0, 8.5, 9.5) reflect commonly accepted RPE
interpretations in resistance training literature:
- Below 7: submaximal, significant reserve remaining
- 7–8.5: productive hypertrophy range, optimal stimulus
- 8.5–9.5: high effort, recovery cost increasing
- Above 9.5: approaching or at failure, unsustainable across sessions

**Differentiated increments by exercise type** reflect practical loading
constraints. A 2.5kg jump on a cable lateral raise is proportionally enormous
and will break the rep range immediately. A 2.5kg jump on bench press is
standard practice.

---

## Alternatives considered

**RPE-only progression — rejected.**
Purely subjective. Difficult to reason about, difficult to debug, and
disconnected from objective performance data already captured in the model.

**Fixed deterministic progression with no RPE — rejected.**
Ignores autoregulation entirely. The system is explicitly designed as a
hybrid engine. A purely deterministic system also has no mechanism to
flag when a load is too easy or unsustainably heavy.

**Percentage-based increments — rejected.**
Introduces floating point load values (e.g. 81.6kg) that do not correspond
to standard plate increments. Fixed kg increments are simpler, auditable,
and practically meaningful.

**Separate deload logic — deferred.**
Deload detection (e.g. three consecutive decrease decisions) is a valid
future feature but is out of scope for the MVP engine. The decrease outcome
provides the signal; deload scheduling can be layered on top later.

---

## Consequences

- The progression engine can be implemented as a pure function:
  WorkoutSession + Program → list[ProgressionDecision]
- All inputs required by the ruleset are already present in the existing models
- The ruleset is auditable: every ProgressionDecision.reason can cite which
  rule fired
- Differentiated increments require exercise_type on Exercise, confirming
  ADR-006 was correctly scoped
- RPE thresholds and load increments are constants that should live in a
  single config location, not scattered through engine code
