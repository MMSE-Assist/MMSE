# Telephone MMSE (T-MMSE) — Audio Agent Edition

**Telephone-administered Mini-Mental State Examination** optimized for **audio-only LLM agents**.

This project implements **T-MMSE exclusively** with prompts optimized for reliable LLM agent behavior. Prompts are **minimal, clear, and direct** to prevent agent confusion. It is not a standard in-person MMSE; it is optimized for telephone administration with 7 core sections (24 points max).

## Quick Start

```bash
cd /home/aleksandrstadnikov/MMSE
uv install
uv venv
uv sync
uv run streamlit run main.py
```

The application launches a Streamlit UI that guides the patient through the assessment via interactive dialogue. All prompts are optimized for robust LLM agent behavior.

## Prompting Philosophy: Simplicity Over Detail

Our prompts are **deliberately simplified** for reliable LLM agent behavior:

✅ **Short** — ~50 lines per prompt (not 200+)  
✅ **Structured** — TASK, IMPORTANT, STEPS, SCORING, TONE  
✅ **Direct** — Commands, not requests  
✅ **Atomic** — One clear task per section  
✅ **Explicit** — Status flags always clear (`NOT_PROCESSED` → `FINISHED`)  

❌ **Avoid** — Edge cases, nested logic, decorative language  

**Why?** LLM agents perform best with minimal, clear instructions. Overcomplicated prompts → agent confusion and errors.

See [PROMPTING_GUIDE.md](PROMPTING_GUIDE.md) for detailed principles and design rationale.

## What Is T-MMSE?

Telephone MMSE is a modified version of the standard Mini-Mental State Examination designed for remote administration:

| Aspect | Standard MMSE | Telephone MMSE |
|--------|---------------|----------------|
| **Format** | In-person | Voice-only (phone) |
| **Sections** | 11 | 7 (see below) |
| **Max Score** | 30 | 24 |
| **Visual Stimuli** | Yes (cards, paper) | None |
| **Writing/Drawing** | Yes | No |
| **Suitable for** | Clinical office, care facility | Remote screening, home |

## T-MMSE Sections (7 items, 24 points)

1. **Orientation to Time** (5 pts) — Year, season, month, date, day of week
2. **Orientation to Place** (5 pts) — Country, state, city, building, floor
3. **Registration** (3 pts) — Immediate recall of 3 spoken words
4. **Attention & Calculation** (5 pts) — Serial 7s or spelling WORLD backwards
5. **Recall** (3 pts) — Delayed recall of the 3 words from Registration
6. **Naming** (2 pts) — Identify objects by verbal description (not visual)
7. **Repetition** (1 pt) — Repeat phrase "No ifs, ands, or buts"

**Total: 24 points**

## What Was Removed (and Why)

- **Three-Stage Command** (3 pts) — Requires handing paper and observing physical manipulation
- **Reading** (1 pt) — Requires showing written instruction on paper
- **Writing** (1 pt) — Requires patient to write and examiner to view/assess handwriting
- **Drawing** (1 pt) — Requires visual stimulus (pentagons) and assessment of visual-spatial copying

These items are impossible or impractical to administer remotely by voice alone.

## Audio Agent Design Notes

This implementation is **specifically optimized for LLM agent behavior**:

- Each prompt is **minimal** (50 lines vs. 200+ in standard versions) to reduce cognitive load
- Prompts use **explicit structure**: TASK | IMPORTANT | STEPS | SCORING | TONE
- Status flags are **always clear**: `NOT_PROCESSED` → asking questions; `FINISHED` → move to next section
- Questions are **one per agent turn** to enable natural conversation flow
- Responses are **scored verbally** with no visual validation needed

**What this means**: If your agent struggles with complex instructions, it will perform well with these minimal, atomic prompts.

See [EXAMPLE_DIALOGUE.md](EXAMPLE_DIALOGUE.md) for a complete sample T-MMSE session.

## Scoring & Interpretation

- **24–21** — Normal cognition (adjust cutoffs per clinical literature)
- **20–11** — Mild cognitive impairment (suggestive, not diagnostic)
- **≤10** — Possible moderate-to-severe impairment (refer for further evaluation)

*Note: These ranges are illustrative; consult published T-MMSE or TICS normative data for your population.*

## Project Structure

```
MMSE/
├── README.md                          (this file)
├── TELEPHONE_MMSE.md                  (detailed T-MMSE clinical docs)
├── PROMPTING_GUIDE.md                 (why prompts are minimal)
├── EXAMPLE_DIALOGUE.md                (sample complete T-MMSE session)
├── main.py                            (Streamlit entry point)
├── pyproject.toml                     (Python dependencies)
├── mmse_graph/
│   └── mmse_construct_update/
│       ├── graph_mmse_only_update.py  (LangGraph workflow: 7 T-MMSE agents, no toggle)
│       ├── mmse_intake_agent.py       (Intake/consent)
│       ├── mmse_basic_agent.py        (Agent template)
│       └── local_system_prompt/
│           ├── intake.txt             (welcome & consent — optimized for audio)
│           ├── orientation_time.txt   (5 questions — minimal)
│           ├── orientation_place.txt  (5 questions — minimal)
│           ├── registration.txt       (3 words — minimal)
│           ├── attention_calculation.txt (serial 7s or spelling — minimal)
│           ├── recall.txt             (recall 3 words — minimal, atomic)
│           ├── naming.txt             (verbal descriptions, not visual)
│           └── repetition.txt         (1 phrase — minimal)
```

## Technical Details

- **Framework**: LangGraph (agent-based workflow)
- **LLM**: NVIDIA ChatNVIDIA (via AGENT_LLM_MODEL env var)
- **UI**: Streamlit
- **Language**: Python 3.10+

The application uses a graph-based agent system where each T-MMSE section is handled by a separate agent that:
1. Loads its section-specific prompt
2. Conducts the assessment
3. Records the score and reasoning
4. Signals completion

## Configuration

Set the following environment variables in `vars.local.env`:

```bash
NVIDIA_API_KEY=<your-api-key>
AGENT_LLM_MODEL=<model-name>
AGENT_LLM_BASE_URL=<base-url>
```

See `vars.env` or `vars.local.env` template for all available options.

## References

- **MMSE**: Folstein, M. F., Folstein, S. E., & McHugh, P. R. (1975). "Mini-Mental State": a practical method for grading the cognitive state of patients for the clinician. *Journal of Psychiatric Research*, 12(3), 189–198.
- **Telephone Versions**: TICS (Brandt et al., 1988), T-MMSE adaptations in literature
- **This Implementation**: Optimized for voice-only cognitive screening without clinical validation claims.

## Important Notes

- This is a **voice-only implementation** of a cognitive screening test; it is not a substitute for a full in-person clinical evaluation.
- Scoring cutoffs provided are illustrative and should be adjusted per your clinical setting and population.
- For clinical use, ensure appropriate clinical supervision and follow-up procedures.
- All prompts are **optimized for LLM agent robustness**; they are minimal and direct to prevent agent confusion.

---

**Last Updated**: March 2026 | **Version**: T-MMSE Audio Agent v1.0 | **Principle**: Minimal Prompts → Robust Behavior
