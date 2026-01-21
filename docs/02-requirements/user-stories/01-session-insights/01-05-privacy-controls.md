# 01-05: Privacy Controls

**Epic:** [01. Session Insights](../../epics/01-session-insights.md)
**Status:** ✅ Implemented

---

## User Story

**As a** user who works with sensitive information,
**I want** control over what data is collected and shared,
**So that** I can use session learning without privacy concerns.

---

## Done Looks Like

1. Privacy level configuration:
   - `self` (default): All data stays local, nothing shared
   - `team`: Summaries can be shared with team
   - `public`: Anonymized metrics can be shared
2. Granular controls:
   - Include/exclude file paths
   - Include/exclude code snippets
   - Include/exclude specific projects
3. Clear indication of what's being captured
4. Easy to disable entirely
5. No data sent anywhere without explicit consent

---

## Why This Matters

**The Problem:** Session transcripts contain sensitive information—code, credentials, business logic. Users won't adopt a tool they don't trust with their data.

**This Fix:** Privacy-first design with granular controls and clear defaults.

**The Result:** Users can benefit from session learning while maintaining control over their data.

---

## Dependencies

**Requires:**
- Configuration system
- Redaction capabilities
- Clear documentation of data handling

**Enables:**
- Team sharing (with consent)
- Confident adoption

---

## Implementation History

| Version | Date | Person | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-01-21 | Chris Park | Initial privacy config with levels and granular controls |

---

**Epic:** [01. Session Insights](../../epics/01-session-insights.md)
