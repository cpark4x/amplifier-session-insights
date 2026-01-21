# 01-03: Data Collection

**Epic:** [01. Session Insights](../../epics/01-session-insights.md)
**Status:** ✅ Implemented

---

## User Story

**As a** user who wants to understand my AI usage patterns,
**I want** useful data collected from each session,
**So that** I can track trends and identify patterns over time.

---

## Done Looks Like

1. Session metrics extracted automatically:
   - Duration
   - Turn count
   - Tool usage (which tools, how often)
   - Files read/modified
   - Token usage
   - Errors encountered
2. Context captured:
   - Project/working directory
   - Git branch (if applicable)
   - Related sessions
3. Classification assigned:
   - Primary task type (debugging, planning, feature, etc.)
   - Domain
   - Complexity level
4. All data stored in structured format (JSON)

---

## Why This Matters

**The Problem:** You have no visibility into how you actually use AI tools. Can't answer "how much time do I spend debugging?" or "which tools do I use most?"

**This Fix:** Automatic data collection creates a queryable record of your AI usage.

**The Result:** Data foundation for personal analytics and pattern detection.

---

## Dependencies

**Requires:**
- Access to events.jsonl
- Access to session metadata
- Git integration (optional, for context)

**Enables:**
- Trend analysis
- Pattern detection
- Usage insights

---

## Implementation History

| Version | Date | Person | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-01-21 | Chris Park | Initial metrics extraction (duration, turns, tools, tokens) |

---

**Epic:** [01. Session Insights](../../epics/01-session-insights.md)
