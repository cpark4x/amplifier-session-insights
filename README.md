# Session Learning

**A system that helps people improve how they work with AI by capturing insights from every session and turning them into actionable learning.**

## What It Does

When an AI session ends, Session Learning automatically:
1. **Extracts metrics** - Duration, tools used, files modified, tokens consumed
2. **Generates insights** - Summary, what went well, areas to improve, tips
3. **Stores locally** - Privacy-first, all data stays on your machine

## Quick Start

### 1. Install the module

```bash
cd modules/hooks-session-learning
pip install -e .
```

### 2. Enable in config

Add to `~/.amplifier/config.yaml`:

```yaml
modules:
  hooks-session-learning:
    min_turns_for_analysis: 3
    min_duration_seconds: 60
```

### 3. Use Amplifier normally

Insights are generated automatically when sessions end.

### 4. Review insights

```bash
ls ~/.amplifier/insights/sessions/
cat ~/.amplifier/insights/sessions/<session-id>.json
```

## Documentation

See [docs/](docs/) for full documentation:

- [Vision](docs/01-vision/01-VISION.md) - What we're building and why
- [Principles](docs/01-vision/02-PRINCIPLES.md) - How we make decisions
- [Success Metrics](docs/01-vision/03-SUCCESS-METRICS.md) - How we measure success
- [Requirements](docs/02-requirements/) - Epics and user stories

## Project Structure

```
session-learning/
├── README.md                 # This file
├── docs/                     # Documentation
│   ├── 01-vision/           # Vision, principles, metrics
│   ├── 02-requirements/     # Epics and user stories
│   └── 07-templates/        # Doc templates
└── modules/                  # Implementation (future)
    └── hooks-session-learning/
```

## Roadmap

| Version | Focus | Status |
|---------|-------|--------|
| V1 | Personal Insights | 🟡 In Progress |
| V2 | Learning Loop | ⏳ Planned |
| V3 | Team Learning | ⏳ Planned |

## Privacy

- **Default:** All data stays local (`~/.amplifier/insights/`)
- **No network calls** without explicit consent
- **Granular controls** for what's captured and shared

See [Privacy Controls](docs/02-requirements/user-stories/01-session-insights/01-05-privacy-controls.md) for details.
