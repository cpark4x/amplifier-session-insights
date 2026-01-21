# Amplifier Session Insights

**A system that helps people improve how they work with AI by capturing insights from every session and turning them into actionable learning.**

## What It Does

### On-Demand Analysis

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

### Automatic End-of-Session Capture

When a session ends, automatically captures:

| What | Cost | When |
|------|------|------|
| **Metrics** (duration, tools, tokens) | Free (~1KB) | Always (2+ turns) |
| **LLM Insights** (summary, tips) | ~$0.01-0.05 | Substantive sessions (5+ turns, 5+ min) |

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
    # Metrics always saved (cheap)
    always_save_metrics: true
    
    # LLM analysis mode: "automatic", "threshold", "on_demand"
    llm_analysis_mode: "threshold"  # Only substantive sessions
    
  tool-session-insights: {}
```

### 3. Use it!

**During a session:**
```
"Show me my session insights"
```

**After a session:**
```bash
# Metrics (always saved)
ls ~/.amplifier/insights/metrics/

# Full insights (LLM analysis)
ls ~/.amplifier/insights/sessions/
```

## Configuration

### Tiered Capture (Recommended)

```yaml
modules:
  hooks-session-learning:
    # === Metrics (always cheap, ~1KB per session) ===
    always_save_metrics: true
    min_turns_for_metrics: 2
    min_duration_for_metrics: 30  # seconds
    
    # === LLM Analysis (costs tokens) ===
    # Modes:
    #   "automatic"  - Run on all qualifying sessions
    #   "threshold"  - Only substantive sessions (recommended)
    #   "on_demand"  - Never auto-run, only when requested
    llm_analysis_mode: "threshold"
    min_turns_for_llm_analysis: 5
    min_duration_for_llm_analysis: 300  # 5 minutes
```

### LLM Analysis Modes

| Mode | When LLM Runs | Best For |
|------|---------------|----------|
| `automatic` | Every session ≥3 turns | Power users, cost not a concern |
| `threshold` | Sessions ≥5 turns AND ≥5 min | Most users (default) |
| `on_demand` | Only when you ask | Cost-conscious, occasional use |

### Privacy Settings

```yaml
privacy:
  session_learning:
    level: "self"              # "self", "team", "public"
    include_file_paths: true
    include_code_snippets: false
    redact_sensitive: true
```

## Storage

```
~/.amplifier/insights/
├── metrics/           # Lightweight metrics (always saved)
│   └── <session-id>.json
└── sessions/          # Full insights with LLM analysis
    └── <session-id>.json
```

**Storage cost:**
- 1 session = ~1-2 KB
- 100 sessions/month = ~200 KB
- 1 year = ~2.4 MB

## Modules

| Module | Type | Purpose |
|--------|------|---------|
| `hooks-session-learning` | Hook | Auto-capture at session end |
| `tool-session-insights` | Tool | On-demand analysis |

## Documentation

See [docs/](docs/) for full documentation:

- [Vision](docs/01-vision/01-VISION.md) - What we're building and why
- [Principles](docs/01-vision/02-PRINCIPLES.md) - How we make decisions
- [Success Metrics](docs/01-vision/03-SUCCESS-METRICS.md) - How we measure success
- [Requirements](docs/02-requirements/) - Epics and user stories

## Roadmap

| Version | Focus | Status |
|---------|-------|--------|
| V1 | Personal Insights | 🟡 In Progress |
| V2 | Learning Loop | ⏳ Planned |
| V3 | Team Learning | ⏳ Planned |

## Contributing

This project is maintained by [@cpark4x](https://github.com/cpark4x). 

If you're interested in having this included in [Amplifier Foundation](https://github.com/microsoft/amplifier-foundation), please reach out!
