# Example T-MMSE Audio Agent Dialogue

This is an example of how the optimized audio agent should conduct a T-MMSE assessment.

## Example Session

### Section 1: Intake

**Agent:**  
"Hello! I'm here to conduct a short cognitive test with you. What is your first name?"

**Patient:** "John"

**Agent:**  
"Nice to meet you, John. What is your last name?"

**Patient:** "Smith"

**Agent:**  
"Thank you, John Smith. I'll now conduct a brief voice-based cognitive test. Are you ready to begin?"

**Patient:** "Yes, I'm ready."

**Agent (internal):**  
- Set `message = "Let's begin with some questions about the date and time."`
- Set `status = FINISHED`
- Set `to_proceed = true`

---

### Section 2: Orientation to Time

**Agent:**  
"First, I have some questions about today. What year is it?"

**Patient:** "2026"

**Agent (scores: ✓ correct)**  
"Good. What season are we in?"

**Patient:** "Spring"

**Agent (scores: ✓ correct)**  
"What month is it?"

**Patient:** "March"

**Agent (scores: ✓ correct)**  
"What is today's date? Just the day of the month."

**Patient:** "22"

**Agent (scores: ✓ correct)**  
"What day of the week is it?"

**Patient:** "Saturday"

**Agent (scores: ✗ incorrect — it's actually Friday, but patient might think it's Saturday. Agent marks 0)**

**Agent (internal):**
- Score: 4/5
- Reasoning: "Year (✓), season (✓), month (✓), date (✓), day of week (✗)"
- Set `status = FINISHED`
- Say: "Thank you. Now let's move to the next section."

---

### Section 3: Orientation to Place

**Agent:**  
"Now some questions about where you are. What country are we in?"

**Patient:** "United States"

**Agent (scores: ✓ correct)**  
"What state are we in?"

**Patient:** "California"

**Agent (scores: ✓ correct)**  
"What city?"

**Patient:** "San Francisco"

**Agent (scores: ✓ correct)**  
"What place are you at right now?"

**Patient:** "I'm at home"

**Agent (scores: ✓ correct — accepts "home" as valid location)**  
"What floor are you on?"

**Patient:** "I'm on the ground floor, first floor"

**Agent (scores: ✓ correct — accepts this description)**

**Agent (internal):**
- Score: 5/5
- Reasoning: "All correct"
- Set `status = FINISHED`

---

### Section 4: Registration

**Agent:**  
"I'm going to say 3 words. Listen carefully and repeat them back. Ready?"

**Patient:** "OK"

**Agent:**  
"APPLE, TABLE, PENNY. Now please repeat those 3 words."

**Patient:** "Apple, table, penny"

**Agent (scores: ✓ 3/3 correct on first attempt)**  
"Good. I will ask you these words again later. Now let's move on."

**Agent (internal):**
- Score: 3/3
- Reasoning: "All 3 words correct on first attempt"
- Set `status = FINISHED`

---

### Section 5: Attention & Calculation

**Agent:**  
"I'm going to ask you to do some math. Start at 100. Subtract 7, then subtract 7 again from your answer. Keep going and tell me each answer. Stop after 5 answers. Ready?"

**Patient:** "OK"

**Agent:**  
"Start at 100 and subtract 7. What's your first answer?"

**Patient:** "93"

**Agent (scores: ✓ correct)**  
"Good. Now subtract 7 from 93. What's the answer?"

**Patient:** "86"

**Agent (scores: ✓ correct)**  
"Next, subtract 7 from 86."

**Patient:** "79"

**Agent (scores: ✓ correct)**  
"Subtract 7 from 79."

**Patient:** "72"

**Agent (scores: ✓ correct)**  
"Last one. Subtract 7 from 72."

**Patient:** "65"

**Agent (scores: ✓ correct)**

**Agent (internal):**
- Score: 5/5
- Reasoning: "Serial 7s: 93✓, 86✓, 79✓, 72✓, 65✓"
- Set `status = FINISHED`

---

### Section 6: Recall

**Agent:**  
"Earlier I said 3 words: APPLE, TABLE, PENNY. Tell me what those words were."

**Patient:** "Apple, penny, table"

**Agent (scores: ✓ 3/3 correct — order doesn't matter)**

**Agent (internal):**
- Score: 3/3
- Reasoning: "All 3 words recalled correctly (order: apple, penny, table)"
- Set `status = FINISHED`

---

### Section 7: Naming

**Agent:**  
"What do you use to write or draw on paper?"

**Patient:** "A pen"

**Agent (scores: ✓ correct)**  
"What do you wear on your wrist to tell the time?"

**Patient:** "A watch"

**Agent (scores: ✓ correct)**

**Agent (internal):**
- Score: 2/2
- Reasoning: "Writing tool (pen)✓, timepiece (watch)✓"
- Set `status = FINISHED`

---

### Section 8: Repetition

**Agent:**  
"Listen and repeat this phrase exactly: No ifs, ands, or buts."

**Patient:** "No ifs, ands, or buts"

**Agent (scores: ✓ correct)**

**Agent (internal):**
- Score: 1/1
- Reasoning: "Phrase repeated correctly"
- Set `status = FINISHED`

---

### Final Summary (Agent's Internal Calculation)

**Total Score: 23/24**

| Section | Score | Max |
|---------|-------|-----|
| Orientation to Time | 4 | 5 |
| Orientation to Place | 5 | 5 |
| Registration | 3 | 3 |
| Attention & Calculation | 5 | 5 |
| Recall | 3 | 3 |
| Naming | 2 | 2 |
| Repetition | 1 | 1 |
| **TOTAL** | **23** | **24** |

**Agent (final message):**  
"Thank you for completing the cognitive test. Your assessment is now complete. A clinician will review your results."

---

## Key Observations

1. **One question per turn** — Agent doesn't overwhelm patient
2. **Clear scoring** — Agent tracks points as it goes
3. **Simple language** — No medical jargon or confusing phrasing
4. **Status flags** — Agent knows when each section is FINISHED
5. **No repeats** — Agent asks once (except Math: break down into single subtractions for clarity)
6. **Accepts variations** — "I'm on the ground floor" ✓, "apple, penny, table" ✓ (order OK)

---

This dialogue demonstrates the **optimal audio agent behavior** with the simplified, robust prompts.
