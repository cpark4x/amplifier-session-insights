# Epic 01: Session Insights

**Owner:** Chris Park
**Contributors:** -

---

## 1. Summary

Automatically capture and store actionable insights from every AI session. When a session ends, extract metrics, generate LLM-powered analysis, and save structured insights that help users understand what happened and how to improve.

---

## 2. Problem

**What's Broken:**
AI sessions are ephemeral—valuable learning disappears when the session ends:
- No record of what worked or didn't work
- No way to identify patterns in your AI usage
- No feedback loop for improvement
- Same mistakes repeated across sessions

**The Frustration:**
- "I had a great session last week but can't remember what I did differently"
- "I keep making the same mistakes but don't realize it"
- "No idea if I'm actually getting better at working with AI"

**Who's Impacted:**
- Anyone who uses AI assistants regularly
- Users who want to deliberately improve their AI collaboration skills
- Teams trying to build organizational AI capability

---

## 3. Proposed Solution

Automatically generate session insights at the end of every qualifying session:

**Automatic Capture:**
- Hook triggers on `session:end`
- Zero user action required
- Background processing (non-blocking)

**Insight Generation:**
- Extract quantitative metrics (duration, tools, tokens, files)
- LLM analysis for qualitative insights (summary, tips, patterns)
- Effectiveness scoring

**Storage:**
- Local-first (`~/.amplifier/insights/sessions/`)
- Privacy-controlled
- Queryable for future retrieval

**Principle:** Make learning automatic and effortless.

---

## 4. User Stories

### Implemented

| # | Story | Owner | Created | Contributors | Last Updated |
|---|-------|-------|---------|--------------|--------------|
| [01-01](../user-stories/01-session-insights/01-01-session-summary.md) | Session Summary | Chris | 2026-01-21 | - | - |
| [01-02](../user-stories/01-session-insights/01-02-self-evaluation.md) | Self-Evaluation | Chris | 2026-01-21 | - | - |
| [01-03](../user-stories/01-session-insights/01-03-data-collection.md) | Data Collection | Chris | 2026-01-21 | - | - |
| [01-05](../user-stories/01-session-insights/01-05-privacy-controls.md) | Privacy Controls | Chris | 2026-01-21 | - | - |

### Future

- ⏭️ **Learning Loop Injection** - Surface relevant past insights at session start
- ⏭️ **History Access & Search** - Query and browse past session insights
- ⏭️ **Team Learning** - Share insights with team (privacy-controlled)
- ⏭️ **Trend Analysis** - Track improvement over time

---

## 5. Outcomes

**Success Looks Like:**
- Users have a record of every meaningful session
- Users can identify their own patterns (good and bad)
- Users report feeling more aware of their AI collaboration style

**We'll Measure:**
- % of users who review insights
- Accuracy rating of generated summaries
- User-reported value of tips

---

## 6. Dependencies

**Requires:**
- Amplifier hook system (`session:end` event)
- LLM provider for analysis
- Local filesystem for storage

**Enables:**
- Learning loop (V2) - Needs insights to inject
- Team learning (V3) - Needs insights to share
- Trend analysis - Needs historical data

**Blocks:**
- Nothing (foundational epic)

---

## 7. Risks & Mitigations

| Risk | Impact | Probability | Strategic Response |
|------|--------|-------------|-------------------|
| LLM analysis too slow | M | M | Background processing, timeout with fallback |
| Insights feel generic/unhelpful | H | M | Iterate on prompts, gather feedback |
| Privacy concerns deter adoption | H | L | Default to private, clear controls |
| Storage grows unbounded | L | M | Retention policy, summarization |

---

## 8. Open Questions

- [ ] What's the minimum session length worth analyzing? (Currently: 3 turns, 60 seconds)
- [ ] Should users be able to manually trigger re-analysis?
- [ ] How long should insights be retained?

---

## 9. Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-01-21 | Chris Park | Initial epic |
