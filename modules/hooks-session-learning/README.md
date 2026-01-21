# hooks-session-learning

Session analysis and learning insights generation for Amplifier.

## Overview

This hook module analyzes completed sessions and generates actionable learning insights using LLM. Insights are stored locally for future reference and self-improvement tracking.

## Features

- **Automatic Analysis**: Triggers on `session:end` event for qualifying sessions
- **Metrics Extraction**: Captures tool usage, files modified, duration, errors, token usage
- **LLM-Powered Insights**: Generates summaries, identifies patterns, provides actionable tips
- **Privacy-First**: Respects privacy config, defaults to local-only storage
- **Non-Blocking**: Background analysis doesn't delay session end
- **Large Session Handling**: Gracefully handles 100k+ token sessions with sampling

## Configuration

```yaml
modules:
  hooks:
    - module: hooks-session-learning
      source: git+https://github.com/microsoft/amplifier-foundation@main#subdirectory=modules/hooks-session-learning
      config:
        min_turns_for_analysis: 3        # Skip trivial sessions (default: 3)
        min_duration_seconds: 60         # Skip quick Q&A (default: 60)
        max_events_to_process: 1000      # Limit for large sessions (default: 1000)
        analysis_timeout_seconds: 60     # LLM timeout (default: 60)
        run_in_background: true          # Non-blocking (default: true)
        
        privacy:
          level: "self"                  # "self", "team", or "public"
          include_file_paths: true       # Include paths in insights
          include_code_snippets: false   # Include code in analysis
          redact_sensitive: true         # Redact secrets/PII
```

## Privacy Configuration

Privacy can also be set globally in `~/.amplifier/config.yaml`:

```yaml
privacy:
  session_learning:
    level: "self"              # "self" (local only), "team" (shareable), "public" (anonymized)
    include_file_paths: true   # Include file paths in insights
    include_code_snippets: false
    redact_sensitive: true
    max_context_tokens: 50000
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SESSION LEARNING FLOW                              │
└─────────────────────────────────────────────────────────────────────────────┘

  session:end event
        │
        ▼
  ┌─────────────┐     ┌──────────────────────────────────────────────────────┐
  │   Filter    │────▶│ Skip if: turns < 3, duration < 60s, already analyzed │
  └─────────────┘     └──────────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                        METRICS EXTRACTION                                │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
  │  │ events.jsonl│  │ Tool Usage  │  │Files Modified│  │Token Counts │    │
  │  │  (sampled)  │  │   Counts    │  │   & Read    │  │   & Errors  │    │
  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
  └─────────────────────────────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                     CONVERSATION SAMPLING                                │
  │                                                                          │
  │   ┌──────────┐    ┌──────────────┐    ┌──────────┐                     │
  │   │ Opening  │ +  │Middle Sample │ +  │  Recent  │  → Context String   │
  │   │(3 turns) │    │ (3 samples)  │    │(5 turns) │                     │
  │   └──────────┘    └──────────────┘    └──────────┘                     │
  │                                                                          │
  │   Truncation: 8000 chars max, word-boundary aware                       │
  └─────────────────────────────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                        LLM ANALYSIS                                      │
  │                                                                          │
  │   Prompt: metrics + conversation sample                                  │
  │   Output: summary, outcome, what_went_well, areas_to_improve, tips      │
  │   Timeout: 60s (configurable)                                           │
  └─────────────────────────────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                         STORAGE                                          │
  │                                                                          │
  │   ~/.amplifier/insights/sessions/<session-id>.json                      │
  │                                                                          │
  │   Atomic write (temp file → rename)                                     │
  └─────────────────────────────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                    EVENT EMISSION                                        │
  │                                                                          │
  │   session-learning:complete { session_id, outcome, tags }               │
  └─────────────────────────────────────────────────────────────────────────┘
```

## Insights JSON Schema

Insights are stored in `~/.amplifier/insights/sessions/<session-id>.json`:

```json
{
  "session_id": "abc123...",
  "generated_at": "2026-01-21T12:00:00+00:00",
  "metrics": {
    "duration_seconds": 1800,
    "turn_count": 15,
    "tool_usage": {
      "read_file": 12,
      "edit_file": 5,
      "bash": 8,
      "grep": 3
    },
    "files_read_count": 8,
    "files_modified_count": 3,
    "errors_encountered": 1,
    "llm_requests": 15,
    "total_tokens": 125000
  },
  "summary": "Debugging authentication issue in OAuth2 flow. Identified race condition in token refresh logic and implemented fix with proper locking.",
  "outcome": "success",
  "what_went_well": [
    "Systematic debugging approach using grep to find related code",
    "Good use of edit_file for incremental changes",
    "Effective test iteration to verify fix"
  ],
  "areas_to_improve": [
    "Could have used LSP for faster symbol lookup",
    "Multiple reads of same file suggest uncertainty"
  ],
  "tips_for_future": [
    "For concurrency bugs, check for shared state access patterns first",
    "Use grep with -C flag to see surrounding context",
    "Consider writing a minimal reproduction test early"
  ],
  "tags": ["debugging", "oauth", "concurrency", "python"],
  "privacy_level": "self"
}
```

## How It Works

1. **Trigger**: Hook registers for `session:end` event with low priority (runs last)
2. **Filter**: Skips sessions with < 3 turns or < 60 seconds duration
3. **Extract**: Reads `events.jsonl` (with 1000 event limit) to gather metrics
4. **Sample**: Creates representative conversation excerpt using bookend + sampling
5. **Analyze**: Calls LLM with structured prompt for insight generation
6. **Store**: Writes JSON atomically to insights directory
7. **Emit**: Fires `session-learning:complete` for other modules to react

## Error Handling

- **Large sessions**: Limited to 1000 events, conversation sampling prevents context overflow
- **LLM timeout**: 60-second timeout prevents blocking, graceful failure
- **Missing data**: Handles missing transcript.jsonl by falling back to events.jsonl
- **Storage errors**: Logs error but doesn't crash, session end proceeds normally
- **Background mode**: Failures don't block session end in any case

## Events Emitted

| Event | Description | Data |
|-------|-------------|------|
| `session-learning:complete` | Analysis finished | `session_id`, `outcome`, `tags` |

## Related Modules

- `hooks-session-naming`: Generates session names (runs before this hook)
- `hooks-progress-monitor`: Tracks in-session progress patterns
