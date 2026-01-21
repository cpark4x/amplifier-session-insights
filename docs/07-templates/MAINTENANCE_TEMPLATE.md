# Documentation Maintenance

**Purpose:** Ensure documentation stays current through automated pre-PR checks

**Author:** [Team]
**Created:** YYYY-MM-DD

---

## Pre-PR Documentation Checklist

**When:** Before submitting any PR (automated via `/git:submit-pr` command)

**AI verifies:**

### 1. Feature Documentation

**For new features:**
- [ ] User story file created in appropriate epic folder
- [ ] User story has Implementation History entry
- [ ] Epic table updated with new story link
- [ ] Story follows template format

**For feature updates:**
- [ ] User story Implementation History updated with new version
- [ ] Epic table shows contributor if different person

### 2. Epic Accuracy

- [ ] Epic "Implemented" section matches actual user story files
- [ ] Epic "Future" section current (not listing implemented work)
- [ ] Epic links work correctly

### 3. Feedback Processing

- [ ] FEEDBACK.md items addressed (if any were resolved)
- [ ] Resolved items moved to Resolved section with links
- [ ] No stale "In Progress" items

### 4. No Orphaned Code

- [ ] Every implemented feature has user story
- [ ] No undocumented features in codebase
- [ ] Code changes align with user story requirements

---

## What Gets Updated When

**When completing a user story:**
1. Add version entry to story's Implementation History table
2. Update epic table if new story
3. Update FEEDBACK.md if resolving logged items

**When starting new epic:**
1. Create epic file from template
2. Create user story folder (XX-epic-name/)
3. Add epic to docs/README.md epic index

**When discovering issues:**
1. Can fix immediately? → Fix, add to Implementation History
2. Needs product decision? → Log to FEEDBACK.md

---

## AI Instructions

**Before creating PR:**
1. Run through checklist above
2. Block PR if critical items missing (user story for new feature)
3. Warn if optional items missing (FEEDBACK.md processing)
4. Generate PR description including doc updates made

**Tell user:** "Documentation updated and verified for PR"

---

## Team Responsibilities

**Developers:** Tell AI when work completes, AI handles doc updates

**Product:** Review FEEDBACK.md weekly, decide on logged items

**Everyone:** Flag drift immediately if docs don't match reality

---

**This process keeps docs current without manual maintenance burden.**
