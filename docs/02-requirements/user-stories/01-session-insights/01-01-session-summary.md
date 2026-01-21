# 01-01: Session Summary

**Epic:** [01. Session Insights](../../epics/01-session-insights.md)
**Status:** ✅ Implemented

---

## User Story

**As a** user who just finished an AI session,
**I want** an automatic summary of what happened,
**So that** I have a record of my work and can remember what I accomplished.

---

## Done Looks Like

1. When a session ends, a summary is automatically generated
2. Summary captures the main outcome/goal of the session
3. Summary includes key decisions made
4. Summary is concise (2-3 sentences, scannable in <10 seconds)
5. Summary is stored locally for later review

---

## Why This Matters

**The Problem:** Sessions end and you forget what you did. A week later, you can't remember if you finished that feature or what approach you took.

**This Fix:** Automatic summary creates a persistent record without any effort.

**The Result:** You always have a quick reference of what each session accomplished.

---

## Dependencies

**Requires:**
- `session:end` hook trigger
- Session transcript access
- LLM for summary generation

**Enables:**
- Session search/browse (can search summaries)
- Learning loop (can reference past summaries)

---

## Implementation History

| Version | Date | Person | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-01-21 | Chris Park | Initial implementation in hooks-session-learning |

---

**Epic:** [01. Session Insights](../../epics/01-session-insights.md)
