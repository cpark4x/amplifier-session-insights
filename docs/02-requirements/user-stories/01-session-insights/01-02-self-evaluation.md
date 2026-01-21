# 01-02: Self-Evaluation

**Epic:** [01. Session Insights](../../epics/01-session-insights.md)
**Status:** ✅ Implemented

---

## User Story

**As a** user who wants to improve my AI collaboration skills,
**I want** feedback on what went well and what could improve,
**So that** I can deliberately get better over time.

---

## Done Looks Like

1. Each session insight includes "what went well" (patterns to repeat)
2. Each session insight includes "areas to improve" (patterns to avoid)
3. Each session insight includes "tips for future" (actionable advice)
4. Feedback is specific to the session, not generic
5. Effectiveness scores provide quantitative self-assessment

---

## Why This Matters

**The Problem:** Without feedback, you can't deliberately improve. You repeat mistakes without realizing and don't know what's working.

**This Fix:** Automatic evaluation surfaces patterns you wouldn't notice yourself.

**The Result:** A feedback loop that enables deliberate practice with AI tools.

---

## Dependencies

**Requires:**
- Session transcript for context
- LLM for evaluation
- Conversation sampling for accurate assessment

**Enables:**
- Pattern detection across sessions
- Personal improvement tracking

---

## Implementation History

| Version | Date | Person | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-01-21 | Chris Park | Initial implementation with what_went_well, areas_to_improve, tips_for_future |

---

**Epic:** [01. Session Insights](../../epics/01-session-insights.md)
