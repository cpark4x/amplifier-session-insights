# Session Learning: Success Metrics

**How we measure if Session Learning is achieving its vision**

**Owner:** Chris Park
**Contributors:** -

**Last Updated:** 2026-01-21

---

## Summary

Session Learning success is measured by whether users actually improve their AI collaboration over time. The primary indicator is self-reported effectiveness improvement. We focus on learning outcomes, not usage metrics—we don't care how often the tool is used, we care if it helps.

---

## Table of Contents

1. [Primary Success Indicator](#primary-success-indicator)
2. [V1 Metrics](#v1-metrics-personal-insights)
3. [V2 Metrics](#v2-metrics-learning-loop)
4. [V3 Metrics](#v3-metrics-team-learning)
5. [User Satisfaction Signals](#user-satisfaction-signals)
6. [What We Don't Measure](#what-we-dont-measure)
7. [Success Criteria by Phase](#success-criteria-by-phase)

---

## Primary Success Indicator

**"Are users getting better at working with AI over time?"**

This is the north star. Everything else supports this. If insights are generated but users don't improve, we've failed. If users improve, we've succeeded—regardless of other metrics.

---

## V1 Metrics: Personal Insights

**Phase Goal:** Validate that automatically captured insights are valuable to users.

### Leading Indicators (Predict Success)

**Engagement:**
- Users review insights after sessions: Target 30%+ of sessions
- Users read full insight (not just glance): >15 seconds view time
- Users reference past insights: Any return visits

**Quality Signals:**
- Insights capture what actually happened: User confirms accuracy
- Tips are relevant to the session: User finds applicable
- Effectiveness scores feel accurate: Within 1 point of user self-assessment

### Lagging Indicators (Measure Success)

**Value Perception:**
- Users keep the feature enabled: >80% retention after 2 weeks
- Users recommend to others: Any organic referrals
- Users request more features: Signal of perceived value

**Actual Improvement:**
- Self-reported effectiveness: Users feel more effective (survey)
- Session quality trends: Effectiveness scores improve over time

### Qualitative Signals

**User Quotes We Listen For:**
- "Oh, that's a good point—I didn't realize I was doing that"
- "This tip actually helped in my next session"
- "I like seeing the summary of what I accomplished"

**Red Flags:**
- "The insights are too generic"
- "This doesn't capture what actually happened"
- "I turned it off because it slowed things down"

---

## V2 Metrics: Learning Loop

**Phase Goal:** Prove that surfacing past insights improves future sessions.

### Leading Indicators

**Context Injection:**
- Relevant past insights surfaced: Match rate to current session type
- Users find injected context helpful: >50% report value

**Pattern Recognition:**
- Recurring patterns detected: System identifies user tendencies
- Patterns are accurate: User confirms observations

### Lagging Indicators

**Effectiveness Improvement:**
- Session effectiveness scores trend upward over 30 days
- Users report feeling more effective (monthly survey)
- Time-to-goal decreases for similar tasks

**Behavioral Change:**
- Users apply tips from past sessions
- Anti-patterns decrease in frequency

---

## V3 Metrics: Team Learning

**Phase Goal:** Demonstrate that shared learning accelerates team improvement.

### Leading Indicators

**Sharing Adoption:**
- Users enable team sharing: >30% of team members
- Team members view shared insights: Regular engagement

### Lagging Indicators

**Team Improvement:**
- New member ramp-up time decreases
- Team-wide effectiveness scores improve
- Best practices spread (pattern adoption rate)

---

## User Satisfaction Signals

### Quantitative

**Net Promoter Score (NPS):**
- Target: 40+ (for V1)
- Segment by: Usage frequency, session types, user role

**Perceived Value:**
- "Did insights help you improve?" (1-5 scale)
- "Would you miss this if removed?" (Yes/No)

### Qualitative

**Validation Statements:**
- "I actually learned something about my workflow"
- "The tips are specific and useful"
- "I feel like I'm getting better at this"

**Concern Statements:**
- "This feels like surveillance"
- "The insights are obvious/not useful"
- "I don't trust the privacy settings"

---

## What We Don't Measure

**Intentionally excluded metrics that would distort behavior:**

### ❌ Number of Insights Generated

**Why not:** More insights ≠ better insights. Would incentivize quantity over quality.

### ❌ Session Count / Usage Frequency

**Why not:** We want users to be more effective, not to use the tool more. High usage could mean dependency, not value.

### ❌ Data Volume Collected

**Why not:** Collecting more data isn't the goal. Would incentivize surveillance over learning.

### ❌ Time Spent Reviewing Insights

**Why not:** Quick, actionable insights are better than lengthy ones requiring long review.

### ❌ Feature Adoption Percentage

**Why not:** Not all features matter equally. Would incentivize feature bloat.

---

## Success Criteria by Phase

### V1 Success = Insights Are Valuable

**Must achieve:**
- >50% of users keep feature enabled after 2 weeks
- >30% of users review insights at least occasionally
- Accuracy rating >3.5/5 on "captures what happened"

**Qualitative validation:**
- At least 3 users report an insight helped them
- No major privacy concerns raised
- No reports of workflow disruption

**Strategic validation:**
- Proof that automatic capture works
- Insights on what makes insights valuable
- Understanding of privacy comfort levels

### V2 Success = Learning Loop Works

**Must achieve:**
- >40% of users report feeling more effective after 30 days
- Measurable improvement in effectiveness scores over time
- Users can cite specific tips that helped

**Qualitative validation:**
- Users reference past insights in conversations
- Users notice when system surfaces relevant context
- Behavioral changes observable in session patterns

### V3 Success = Teams Learn Faster

**Must achieve:**
- Team-enabled groups show faster effectiveness improvement
- New member ramp-up time measurably decreases
- >30% of team members actively share insights

**Qualitative validation:**
- Teams report value from shared learning
- Best practices demonstrably spread
- No privacy incidents or trust erosion

---

## Measuring What Matters

### The Questions We Keep Asking

**After every user interaction:**
- Did this insight help you? (thumbs up/down)
- Was this tip applicable? (yes/no)
- Anything we missed? (optional feedback)

**After every week (for active users):**
- Do you feel more effective than last week?
- Which insight was most valuable?
- What would make this more useful?

**After every month:**
- Are we seeing improvement trends?
- What patterns are emerging?
- Are users getting value or just using it?

### The Standard

**"If a metric doesn't help us answer 'are users getting better?', we don't track it."**

We resist the temptation to measure everything. Metrics should inform product decisions, not justify existence.

---

## Related Documentation

**Vision folder (strategic context):**
- [01-VISION.md](./01-VISION.md) - Strategic vision and positioning
- [02-PRINCIPLES.md](./02-PRINCIPLES.md) - Implementation philosophy

**Implementation:**
- [Epic 01: Session Insights](../02-requirements/epics/01-session-insights.md)

---

## Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-01-21 | Chris Park | Initial success metrics document |
