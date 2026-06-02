# System Design (how it works)

## Core Loop

The system operates in a continuous feedback loop:

Input (performance data)
→ Program Generator
→ Workout Execution
→ Logging Layer
→ Progression Engine
→ Updated Program
→ repeat

---

## Core Components

### 1. Program Definition
Defines fixed structure:
- exercise selection
- sets and rep ranges
- training split

This remains stable across cycles - predefined by user
this is recommended to be done by iterating with AI or from online programs/ coach
this is a step that requires personalisation according to specific user requirements

---

### 2. Workout Execution Layer
Represents real-world training sessions.

Captured data:
- exercise
- sets
- reps
- load
- optional RPE/RIR

---

### 3. Progression Engine (Hybrid)

Combines:

#### Deterministic rules:
- progression based on rep range completion
- load increases after performance thresholds
- deload conditions (conditional to fatigue defined by recent gym usage)

#### Autoregulation layer:
- modifies progression rate based on RPE/RIR
- adjusts aggressiveness of load increases
- this is added to achieve gradual and optimal hypertrophy (as advised by consultation from CLAUDE)

---

### 4. Data Layer
Stores:
- workout history
- program history
- progression decisions

Format: CSV / JSON (initially)

---

## Design Philosophy

- Simplicity over optimisation
- Interpretability over complexity
- Deterministic core with adaptive modifiers
