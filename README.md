# Amplifier Session Insights

**A system that helps people improve how they work with AI by capturing insights from every session and turning them into actionable learning.**

## What It Does

### On-Demand Analysis (New!)

Ask for insights anytime during a session:

```
"How's this session going?"
"Show me session insights"
"What are my metrics so far?"
```

You'll get:
- **Duration & turns** - How long, how many exchanges
- **Tool usage** - What tools you're using most
- **Pace assessment** - Fast, moderate, or deliberate
- **Tips** - Contextual suggestions for improvement

### Automatic End-of-Session Analysis

When a session ends, automatically captures:
1. **Metrics** - Duration, tools used, files modified, tokens consumed
2. **Insights** - Summary, what went well, areas to improve, tips
3. **Storage** - Privacy-first, all data stays on your machine

## Quick Start

### 1. Install both modules

```bash
cd ~/projects/amplifier-session-insights/modules

# Hook for automatic end-of-session capture
cd hooks-session-learning && pip install -e . && cd ..

# Tool for on-demand analysis
cd tool-session-insights && pip install -e . && cd ..
```

### 2. Enable in config

Add to `~/.amplifier/config.yaml`:

```yaml
modules:
  hooks-session-learning:
    min_turns_for_analysis: 3
    min_duration_seconds: 60
  tool-session-insights: {}
```

### 3. Use it!

**During a session:**
```
"Show me my session insights"
```

**After a session:**
```bash
ls ~/.amplifier/insights/sessions/
cat ~/.amplifier/insights/sessions/<session-id>.json | jq
```

## Modules

| Module | Type | Purpose |
|--------|------|---------|
| `hooks-session-learning` | Hook | Auto-capture insights at session end |
| `tool-session-insights` | Tool | On-demand analysis during sessions |

## Documentation

See [docs/](docs/) for full documentation:

- [Vision](docs/01-vision/01-VISION.md) - What we're building and why
- [Principles](docs/01-vision/02-PRINCIPLES.md) - How we make decisions
- [Success Metrics](docs/01-vision/03-SUCCESS-METRICS.md) - How we measure success
- [Requirements](docs/02-requirements/) - Epics and user stories

## Project Structure

```
amplifier-session-insights/
├── README.md                 # This file
├── docs/                     # Documentation
│   ├── 01-vision/           # Vision, principles, metrics
│   ├── 02-requirements/     # Epics and user stories
│   └── 07-templates/        # Doc templates
└── modules/
    ├── hooks-session-learning/   # End-of-session capture
    └── tool-session-insights/    # On-demand analysis
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

## Contributing

This project is maintained by [@cpark4x](https://github.com/cpark4x). 

If you're interested in having this included in [Amplifier Foundation](https://github.com/microsoft/amplifier-foundation), please reach out!
