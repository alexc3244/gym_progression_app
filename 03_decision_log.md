# Decision Log

# Incredibly important documentation which captures decesions made for development (largely in consult with CLAUDE/ CHATGPT

## D001: Rule-based vs ML-based system

Decision: Rule-based + autoregulation (hybrid)

Rationale:
- Gym progression is relatively structured and rule-driven
- ML models would add unnecessary complexity early
- Interpretability is more valuable than prediction accuracy
- Rationale should be based on simple and therefore clear logic

---

## D002: Data storage format

Decision: CSV / JSON

Rationale:
- Lightweight
- Human-readable
- Easy to debug progression behaviour
- No need for database at MVP stage

---

## D003: Fixed exercise selection

Decision: Exercises are predefined by user

Rationale:
- most importantly this is a very complex process and highly specific to user requirements
- secondly, there is no black/white "best" program and depends on which schools of thought one belives in the most
- Reduces complexity of program generation
- Focus remains on progression logic rather than exercise selection
- Allows cleaner evaluation of engine behaviour

---

## D004: No frontend at MVP stage

Decision: CLI / script-based interface only

Rationale:
- Faster iteration
- Keeps focus on engine logic
- UI decoupled from core system
- allows quicker dev of backend creation and to exercise good process better

---

## D005: Autoregulation via RPE/RIR only

Decision: Use RPE/RIR as sole subjective signal

Rationale:
- Standard in hypertrophy programming
- Easy to collect without additional hardware (remember no integration with fitbits, sleep score etc)
- Sufficient signal for load adjustment
