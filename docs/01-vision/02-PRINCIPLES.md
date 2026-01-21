# Session Learning: Principles

**The principles that guide every implementation decision in Session Learning.**

These are not generic software principles—they're specific to building a system that helps people learn from their AI sessions.

**Owner:** Chris Park
**Contributors:** -

**Last Updated:** 2026-01-21

---

## Summary

Session Learning principles cover four areas: how we think about the product (learning over analytics), how we build it (simple v1, iterate), how we handle privacy (consent-first), and how we work (ship and learn). The decision framework helps AI choose correctly when building features.

---

## Table of Contents

1. [Core Product Principles](#core-product-principles)
2. [Technical Principles](#technical-principles)
3. [Privacy Principles](#privacy-principles)
4. [Development Principles](#development-principles)
5. [Anti-Patterns](#anti-patterns)
6. [Decision Framework](#decision-framework)

---

## Core Product Principles

These principles define what makes Session Learning different.

### 1. Learning Over Analytics

**What it means:** Every feature should help users improve, not just measure what happened.

**How it guides decisions:**
- Build features that create actionable insights ✅
- Surface patterns that help users get better ✅
- Add metrics that inform improvement ✅
- Build dashboards that just show numbers ❌
- Track data without a learning purpose ❌

**Example applications:**
- "You spent 2 hours" → ❌ Analytics
- "You're most effective in short focused sessions" → ✅ Learning
- "45 tool calls" → ❌ Analytics
- "You iterate faster when you read files before editing" → ✅ Learning

**Decision rule:** If a feature doesn't answer "how can I get better?", reconsider it.

---

### 2. Zero-Effort Capture

**What it means:** Insights should be captured automatically, never requiring user action.

**How it guides decisions:**
- Trigger capture automatically at session end ✅
- Extract insights without user prompts ✅
- Work silently in the background ✅
- Require users to click "save insights" ❌
- Ask users to tag or categorize sessions ❌

**Example applications:**
- Hook triggers on `session:end` automatically
- Insights generated without user intervention
- No "would you like to save insights?" prompts

**Decision rule:** If it requires user action to capture, find another way.

---

### 3. Actionable Over Comprehensive

**What it means:** Better to surface 3 actionable insights than 20 data points.

**How it guides decisions:**
- Prioritize insights users can act on ✅
- Keep summaries scannable (< 30 seconds to read) ✅
- Focus on patterns, not exhaustive detail ✅
- Include every metric we can extract ❌
- Generate lengthy analysis documents ❌

**Example applications:**
- "Tip: In this codebase, check tests before modifying" → ✅ Actionable
- "You made 47 file edits across 12 directories" → ❌ Just data
- "Area to improve: Narrow debugging scope earlier" → ✅ Actionable

**Decision rule:** If you can't act on it in the next session, it's not valuable.

---

## Technical Principles

How we build the system.

### 1. Simple V1, Iterate

**What it means:** Ship the simplest thing that provides value, then improve based on usage.

**How it guides decisions:**
- Build minimal viable feature first ✅
- Skip features until proven needed ✅
- Let user feedback drive iteration ✅
- Build comprehensive system upfront ❌
- Add features "just in case" ❌

**Example applications:**
- V1: Just session insights stored as JSON files
- Skip: Index files, pattern databases, team features
- Add later: Whatever users actually ask for

**Decision rule:** When in doubt, leave it out. Add when there's pull.

---

### 2. Graceful Degradation

**What it means:** Session Learning should never break the user's session or workflow.

**How it guides decisions:**
- Run analysis in background, non-blocking ✅
- Fail silently if analysis fails ✅
- Session ends normally even if insights fail ✅
- Block session end waiting for analysis ❌
- Crash on analysis errors ❌

**Example applications:**
- LLM timeout? Store metrics-only insight, continue.
- Storage error? Log warning, continue.
- Never: "Session ended but insights failed, please wait..."

**Decision rule:** The user's work is more important than our features.

---

### 3. Local-First Storage

**What it means:** All data stays on the user's machine unless they explicitly share.

**How it guides decisions:**
- Store insights in `~/.amplifier/insights/` ✅
- Query local files for history ✅
- Never send data without consent ✅
- Default to cloud storage ❌
- Require network for basic features ❌

**Example applications:**
- Insights stored as local JSON files
- No network calls for personal features
- Team sync is opt-in, not default

**Decision rule:** If it works offline, it's designed correctly.

---

## Privacy Principles

How we handle sensitive session data.

### 1. Consent Before Collection

**What it means:** Users explicitly choose what's collected and shared.

**How it guides decisions:**
- Default to minimum collection ✅
- Require opt-in for sharing ✅
- Make privacy settings obvious ✅
- Collect everything by default ❌
- Hide sharing in settings ❌

**Example applications:**
- Default privacy level: "self" (nothing shared)
- Team sharing requires explicit config change
- Clear indication of what's being captured

**Decision rule:** When in doubt, don't collect.

---

### 2. Granular Sharing Control

**What it means:** Users control exactly what's shared at each level.

**How it guides decisions:**
- Separate controls for summaries, metrics, patterns ✅
- Different settings for team vs public ✅
- Clear preview of what will be shared ✅
- All-or-nothing sharing ❌
- Confusing privacy settings ❌

**Example applications:**
- "Share summaries with team: Yes"
- "Share file paths with team: No"
- "Share anonymized metrics publicly: Yes"

**Decision rule:** Give users the control they need to feel safe.

---

### 3. Anonymization for Aggregation

**What it means:** Any data leaving the user's machine must be anonymized.

**How it guides decisions:**
- Strip identifying information before sharing ✅
- Aggregate patterns, not individual sessions ✅
- Never share raw transcripts ✅
- Share session content externally ❌
- Include file paths in public data ❌

**Example applications:**
- Team sees: "Common pattern: evaluation matrices"
- Team doesn't see: "Chris's session transcript from today"

**Decision rule:** If you can identify the person or project, don't share it.

---

## Development Principles

How we work building this.

### 1. Use It To Build It

**What it means:** We should use Session Learning while building Session Learning.

**How it guides decisions:**
- Dogfood features before releasing ✅
- Let our own pain drive priorities ✅
- Build what we actually need ✅
- Build features we won't use ❌
- Skip testing on real sessions ❌

**Example applications:**
- Enable the hook while developing
- Review our own session insights
- Fix issues we encounter firsthand

**Decision rule:** If we don't use it, users won't either.

---

### 2. Document Decisions

**What it means:** Capture why we built things, not just what we built.

**How it guides decisions:**
- Record decisions in docs ✅
- Explain rationale in code comments ✅
- Update docs when decisions change ✅
- Leave decisions undocumented ❌
- Let code speak for itself on strategy ❌

**Example applications:**
- "We chose JSON files over SQLite because..."
- "Privacy defaults to 'self' because..."
- Decision log in each major doc

**Decision rule:** Future us (and AI) need to understand why.

---

## Anti-Patterns

Patterns that violate our principles and vision.

### ❌ Surveillance Mode

**Bad:** "Track everything users do for analysis"
**Good:** "Capture insights that help users improve"

**Why it's bad:** Violates "Learning Over Analytics" and privacy principles. Users will disable it.

---

### ❌ Analysis Paralysis

**Bad:** Build comprehensive analytics before shipping anything
**Good:** Ship simple insights, iterate based on feedback

**Why it's bad:** Violates "Simple V1, Iterate". We'll build the wrong thing.

---

### ❌ Blocking Behavior

**Bad:** "Please wait while we analyze your session..."
**Good:** Analysis happens in background, user continues

**Why it's bad:** Violates "Graceful Degradation". User's workflow is sacred.

---

### ❌ Default Sharing

**Bad:** Share insights with team by default, let users opt out
**Good:** Keep everything private, let users opt in to sharing

**Why it's bad:** Violates "Consent Before Collection". Breaks trust.

---

### ❌ Comprehensive Capture

**Bad:** Store complete session transcripts in insights
**Good:** Extract actionable patterns, discard raw content

**Why it's bad:** Violates "Actionable Over Comprehensive" and privacy. Creates storage/privacy burden.

---

## Decision Framework

**When AI faces choices, use these criteria:**

### Priority Hierarchy

1. **User's workflow** - Never interrupt or slow down the user
2. **Privacy** - When in doubt, don't collect/share
3. **Actionability** - Insights must be usable
4. **Simplicity** - Simpler solution wins
5. **Comprehensiveness** - Only if above are satisfied

---

### Specific Decision Rules

**If considering adding a new metric:**
→ Only if it helps answer "how can I get better?" Otherwise skip.

**If considering storing more data:**
→ Only if it serves a learning purpose. Raw storage is not valuable.

**If considering a team feature:**
→ Not until V3. Focus on individual learning first.

**If considering blocking behavior:**
→ No. Find an async/background alternative.

**If considering default-on sharing:**
→ No. Always default to private.

**If feature requires user action to capture:**
→ Find automatic alternative. Zero-effort capture is non-negotiable.

---

## Related Documentation

**Vision folder (strategic context):**
- [01-VISION.md](./01-VISION.md) - Strategic vision and positioning
- [03-SUCCESS-METRICS.md](./03-SUCCESS-METRICS.md) - How we measure success

**Implementation:**
- [Epic 01: Session Insights](../02-requirements/epics/01-session-insights.md)

---

## Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-01-21 | Chris Park | Initial principles document |
