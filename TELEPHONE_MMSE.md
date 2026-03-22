# Telephone MMSE (T-MMSE) — Project Format

This MMSE implementation is **exclusively designed for telephone administration** (T-MMSE).
It does not support standard in-person MMSE mode.

## Overview

Telephone MMSE removes four standard MMSE items that cannot be administered remotely:
- **three_stage_command** (requires handing paper, demonstrating folding/placement)
- **reading** (requires showing written instruction on paper)
- **writing** (requires patient to write and examiner to assess handwriting/content)
- **drawing** (requires showing visual stimulus and assessing copied drawing)

## Retained Sections (7 items, 24 points max)

| Section | Points | Format |
|---------|--------|--------|
| Orientation to Time | 5 | Verbal questions (year, season, date, day, month) |
| Orientation to Place | 5 | Verbal questions (country, state, city, building, floor) |
| Registration | 3 | Repeat 3 words verbally (one point each) |
| Attention & Calculation | 5 | Serial 7s or spelling WORLD backwards |
| Recall | 3 | Recall the 3 words from Registration |
| Naming (Verbal) | 2 | Name common objects described verbally (not shown) |
| Repetition | 1 | Repeat phrase "No ifs, ands, or buts" |
| **Total** | **24** | **Telephone-only** |

## Why These Changes?

Standard MMSE = 30 points requires:
- In-person presence
- Visual stimuli cards (for Naming and Reading)
- Paper and pen (for Drawing and Writing)
- Physical demonstration space (for three_stage_command)

**Telephone MMSE** = 24 points adapts to voice-only constraints while preserving:
- Temporal orientation
- Spatial orientation
- Immediate recall (Registration)
- Sustained attention (Calculation)
- Delayed recall (Recall)
- Language comprehension (Repetition, Naming)

## How to Run

```bash
cd /home/aleksandrstadnikov/MMSE
python main.py
```

The application will **only** administer the 7 T-MMSE sections. No configuration needed.

## Scoring

- Minimum score: 0
- Maximum score: **24** (not 30)
- Interpretation guidelines:
  - 24–21: Normal cognition
  - 20–11: Mild cognitive impairment (adjust cutoff as needed for phone-based assessment)
  - ≤10: Possible moderate-to-severe impairment

*Note: These cutoffs are illustrative; consult clinical literature for phone-specific thresholds.*

## Technical Details

- Agent list in `mmse_graph/mmse_construct_update/graph_mmse_only_update.py`: 
  - Function `get_agents_with_types_and_schema()` returns 7 agents (T-MMSE only).
  - Prompts in `local_system_prompt/` are optimized for telephone delivery.

## Future Enhancements

1. **Aggregate Scoring**: Add explicit end-of-test summary that computes total score and provides interpretation.
2. **Naming Refinement**: Consider replacing object naming with category/definition-based verbal naming (e.g., "What is an object you use to tell time?" → watch).
3. **Clinical Validation**: Cross-reference with published T-MMSE or TICS (Telephone Interview for Cognitive Status) literature.
4. **Reporting**: Generate structured report with date, time, score, and flagged items.

---

**Project Status**: T-MMSE only. Standard MMSE (11 items, 30 points) is not supported by this codebase.

