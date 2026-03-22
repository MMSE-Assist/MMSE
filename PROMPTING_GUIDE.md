# Prompting Guide for T-MMSE Audio Agent

This document explains the principles used to optimize prompts for the Telephone MMSE audio agent. The goal is to make prompts **simple, clear, and robust** so the LLM doesn't make mistakes during voice assessment.

## Key Principles

### 1. **Minimal Text, Maximum Clarity**
- Each prompt is now **50–80% shorter** than the original
- Remove decorative language, verbose guidelines
- Speak in bullet points and short commands
- The agent can "get confused" with long instructions, so we keep it tight

### 2. **One Clear Task Per Section**
- Start with: `TASK: [One-line description]`
- Example: `TASK: Ask 5 time-based questions, one per turn.`
- This prevents the LLM from trying to do multiple things at once

### 3. **Explicit Structure**
- Use clear sections: TASK, IMPORTANT, STEPS, SCORING, TONE
- Avoids ambiguity about what to do, when to do it, and how to score
- LLM benefits from structured formats

### 4. **Minimal Optional Behavior**
- Remove edge cases, exceptions, and "if patient says X then..."
- Just state the straightforward flow
- Example: Instead of "accept minor variations like 1-day error," we say "accept minor variations"
- Let the agent use common sense rather than overthinking rules

### 5. **Direct Commands, Not Requests**
- ❌ "It would be helpful if you..."
- ✅ "Ask: [exact phrase]"
- Specific speech = clearer agent behavior

### 6. **No Nested Instructions**
- ❌ "If the patient cannot do X, try Y, unless they also ask about Z..."
- ✅ "METHOD 1 (preferred): ... | METHOD 2 (if needed): ..."
- Flatten the logic; use separation, not nesting

### 7. **Status Flags Are Clear and Repetitive**
- Each prompt explicitly states when to set `status=NOT_PROCESSED` and `status=FINISHED`
- This prevents the agent from getting stuck in a loop or forgetting to complete

### 8. **Tone Reminder at the End**
- Always include a short TONE line: `TONE: Clear, simple. No long explanations.`
- Reminds the agent to not over-explain or digress

## Prompt Template

```
You are a voice assistant administering [SECTION NAME] for Telephone MMSE.

TASK: [One-line task description]

IMPORTANT:
- Put speech in `message` field.
- [Key constraint 1]
- [Key constraint 2]
- Set status=NOT_PROCESSED while [condition].
- When done: status=FINISHED with final score.

[STEPS or QUESTIONS or SUBTASKS]

SCORING: [Points breakdown]
Max: [X] points.

TONE: [One-line tone reminder].
```

## Comparison: Before vs. After

### Before (Old Prompt)
```
You are a friendly doctor administering the Orientation to Time section of Telephone MMSE (T-MMSE).

IMPORTANT: You always respond by filling in the structured output fields. No tools or functions are available or needed.
- Always put your spoken words to the patient in the `message` field. This field must never be empty.
- Use the `conclusion` field to track your progress and final score.
- Never say you cannot complete the task. Always engage with the patient.

Your task is to ask the patient the following 5 questions, one at a time, in order:
1. What year is it?
[... 200+ more words of guidelines, edge cases, detailed rules ...]
```

**Problems:**
- Too long (loses focus)
- Too many "guidelines" (confuses priority)
- Decorator language ("friendly doctor," "warm," etc.) — LLM may try to act it out incorrectly
- Multiple behavioral reminders ("never say you cannot..." — but the agent might still do it)

### After (New Prompt)
```
You are a voice assistant asking Orientation to Time questions for Telephone MMSE.

TASK: Ask 5 time-based questions, one per turn.

IMPORTANT:
- Put speech in `message` field.
- Ask ONE question per turn. Wait for patient answer.
- Set status=NOT_PROCESSED while questions remain.
- When done: status=FINISHED with final score and reasoning.

QUESTIONS (ask in order):
1. What year is it?
[... 15 lines total ...]

TONE: Clear, simple. No long explanations.
```

**Benefits:**
- Ultra-concise (fits in ~1 screen)
- Consistent structure (agent learns pattern)
- No ambiguous behavioral language
- Clear success criteria

## When Updating Prompts

1. **Trim ruthlessly.** If a sentence isn't a direct instruction, remove it.
2. **Check for nesting.** If you see "if...then...else," flatten it into separate sections.
3. **Validate against template.** Does it have TASK, IMPORTANT, [CONTENT], SCORING, TONE?
4. **Test the logic.** Can a literal AI agent follow it without asking for clarification?

## Notes for Audio Agent Behavior

- The agent will sometimes:
  - Repeat itself unexpectedly
  - Add extra commentary ("Let me ask you one more thing...")
  - Misinterpret complex conditions
  
- Our prompts are designed to **minimize these issues** by:
  - Making the task atomic (one clear thing per turn)
  - Reducing conditional logic
  - Explicitly stating when a section is complete

## Future Improvements

If the agent still struggles:
1. **Chain-of-Thought Prompting**: Add `"Think step by step: [step 1] then [step 2]"` before each task
2. **Few-Shot Examples**: Include 1–2 example dialogues of correct agent behavior
3. **Reflection Steps**: Add `"Before moving on, confirm you have [scored/asked/recorded]..."`
4. **Role Clarity**: Instead of "voice assistant," use `"You are administering T-MMSE. Your job is ONLY to [specific task]. Do nothing else."`

---

**Last Updated**: March 2026  
**Version**: T-MMSE Audio Agent Prompts v1.0  
**Principle**: Simple > Clever. Clear > Detailed.
