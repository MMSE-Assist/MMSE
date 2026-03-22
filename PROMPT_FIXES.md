# T-MMSE Prompt Fixes — Edge Case Handling

**Date**: March 22, 2026  
**Purpose**: Address edge cases and ambiguous scenarios identified during testing  
**Philosophy**: Minimal additions, no overloading

---

## Fixed Issues

### 1. **intake.txt** — Handle Patient Refusal ✅
**Problem**: No instruction for when patient declines to begin test.  
**Fix**: Added explicit handling:
```
If patient confirms: set to_proceed=true, status=FINISHED.
If patient declines or is unsure: set to_proceed=false, status=FINISHED. Say: "No problem, we can reschedule."
```
**Impact**: Prevents agent confusion; allows graceful test cancellation.

---

### 2. **orientation_time.txt** — Uncertain Answers ✅
**Problem**: "Accept minor variations" could be interpreted too liberally.  
**Fix**: Added guidance for uncertain answers:
```
For uncertain answers ("I think...", "maybe..."), accept first stated answer anyway.
```
**Impact**: Clarifies that vague answers should still be scored based on the number stated.

---

### 3. **attention_calculation.txt** — Request Clarification ✅
**Problem**: No instruction if patient asks to repeat or wants to know which method to use.  
**Fix**: Added two rules:
```
If patient asks to repeat: repeat instruction ONCE, then ask for answer.
If patient asks which method: choose Serial 7s by default.
```
**Impact**: Prevents agent loops; provides clear decision rules for common scenarios.

---

### 4. **registration.txt** — Extra Words ✅
**Problem**: Unclear how to handle patient adding extra words.  
**Fix**: Clarified scoring:
```
1 point per word on first attempt only (count ONLY the 3 words, ignore additions or omissions of extra words).
```
**Impact**: Clear scoring rule; prevents agent confusion on auxiliary words.

---

### 5. **naming.txt** — Watch vs Clock ✅
**Problem**: "CLOCK" ambiguous (wearable vs wall/desk).  
**Fix**: Specified wearable only:
```
Expected: WATCH or similar wearable timepiece (not desk/wall clock).
Accept reasonable synonyms (ballpoint pen, fountain pen, wristwatch, smartwatch, etc.).
```
**Impact**: Prevents false positives on non-wearable timepieces.

---

### 6. **recall.txt** ✅ No Changes
Already clear and complete. Handles word order flexibility and partial recall correctly.

---

### 7. **repetition.txt** ✅ No Changes
Already clear and atomic. Exact phrase matching requirement is explicit.

---

## Summary

| Prompt | Status | Change Type |
|--------|--------|-------------|
| intake.txt | ✅ Fixed | +2 rules for refusal handling |
| orientation_time.txt | ✅ Fixed | +1 rule for uncertain answers |
| attention_calculation.txt | ✅ Fixed | +2 rules for clarification requests |
| registration.txt | ✅ Fixed | +1 rule clarification (extra words) |
| naming.txt | ✅ Fixed | +1 rule clarification (watch only) |
| recall.txt | ✅ No changes | Already robust |
| repetition.txt | ✅ No changes | Already robust |

**Total Lines Added**: ~15 lines across 5 prompts  
**Total Lines Removed**: 0 (pure additions, no deletion of existing clarity)  
**Overload Risk**: ✅ Minimal — each fix is 1-2 sentences, addresses specific ambiguity

---

## Edge Cases Now Covered

1. ✅ Patient refuses to start test
2. ✅ Patient gives uncertain/vague time answer
3. ✅ Patient asks to repeat attention calculation instruction
4. ✅ Patient asks which calculation method to use
5. ✅ Patient adds extra words during registration recall
6. ✅ Patient names non-wearable clock as timepiece

---

## Testing Recommendation

Before deployment, test these scenarios with your LLM agent:
- [ ] Run full T-MMSE with agent declining at intake
- [ ] Run with patient providing uncertain time answers
- [ ] Run with patient asking "which method?" during attention test
- [ ] Run with patient repeating phrase + extra words during registration
- [ ] Verify watch vs non-wearable clock discrimination

---

**Status**: Ready for integration testing ✅
