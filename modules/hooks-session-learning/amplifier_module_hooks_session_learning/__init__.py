"""Session Learning Hook Module

Analyzes completed sessions and generates actionable insights using LLM.
Stores learning insights to ~/.amplifier/insights/sessions/ for future reference.

Privacy-first design:
- Respects privacy config from ~/.amplifier/config.yaml
- Defaults to "self" only (insights stored locally, not shared)
- Redacts sensitive content before LLM analysis
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from amplifier_core import HookResult

logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================


@dataclass
class PrivacyConfig:
    """Privacy settings for session learning."""

    # Privacy level: "self" (local only), "team" (shareable), "public" (anonymized)
    level: str = "self"
    # Whether to include file paths in insights
    include_file_paths: bool = True
    # Whether to include code snippets in insights
    include_code_snippets: bool = False
    # Whether to redact potential secrets/PII before analysis
    redact_sensitive: bool = True
    # Max content length to send to LLM (prevent huge context)
    max_context_tokens: int = 50000


@dataclass
class SessionLearningConfig:
    """Configuration for session learning analysis."""

    # === Metrics Capture (always cheap) ===
    # Always save metrics regardless of session length
    always_save_metrics: bool = True
    # Minimum turns before saving metrics (even when always_save_metrics=True)
    min_turns_for_metrics: int = 2
    # Minimum duration for metrics (seconds)
    min_duration_for_metrics: int = 30

    # === LLM Analysis (costs tokens) ===
    # LLM analysis mode: "automatic", "threshold", "on_demand"
    #   - automatic: Run LLM analysis on all qualifying sessions
    #   - threshold: Only run LLM analysis on substantive sessions
    #   - on_demand: Never auto-run, only when user requests
    llm_analysis_mode: str = "threshold"
    # Minimum turns for LLM analysis (when mode is "threshold" or "automatic")
    min_turns_for_llm_analysis: int = 5
    # Minimum duration for LLM analysis in seconds (when mode is "threshold")
    min_duration_for_llm_analysis: int = 300  # 5 minutes

    # === Legacy (for backward compatibility) ===
    # These map to the new settings
    min_turns_for_analysis: int = 3  # Maps to min_turns_for_metrics
    min_duration_seconds: int = 60  # Maps to min_duration_for_metrics

    # === Processing Limits ===
    # Maximum events to process (handle large sessions gracefully)
    max_events_to_process: int = 1000
    # Timeout for LLM analysis (don't block forever)
    analysis_timeout_seconds: int = 60
    # Whether to run analysis in background (non-blocking)
    run_in_background: bool = True
    # Privacy settings
    privacy: PrivacyConfig = field(default_factory=PrivacyConfig)


# ============================================================================
# Data Models
# ============================================================================


@dataclass
class SessionMetrics:
    """Extracted metrics from a session."""

    session_id: str
    duration_seconds: float
    turn_count: int
    tool_usage: dict[str, int]  # tool_name -> count
    files_read: list[str]
    files_modified: list[str]
    errors_encountered: int
    llm_requests: int
    total_input_tokens: int
    total_output_tokens: int
    model_used: str | None = None
    started_at: str | None = None
    ended_at: str | None = None


@dataclass
class SessionInsights:
    """Generated insights from session analysis."""

    session_id: str
    generated_at: str
    metrics: dict[str, Any]
    summary: str
    outcome: str  # "success", "partial", "abandoned", "error"
    what_went_well: list[str]
    areas_to_improve: list[str]
    tips_for_future: list[str]
    tags: list[str]  # Auto-generated tags for categorization
    privacy_level: str


# ============================================================================
# Prompts
# ============================================================================


ANALYSIS_PROMPT = """You analyze coding assistant sessions to extract learning insights.

<task>
Analyze this session data and provide structured insights to help the user improve their workflow.
</task>

<session_metrics>
Session ID: {session_id}
Duration: {duration_minutes:.1f} minutes
Turns: {turn_count}
Model: {model}

Tool Usage:
{tool_usage_formatted}

Files Read: {files_read_count}
Files Modified: {files_modified_count}
{files_section}

Errors Encountered: {errors_count}
Token Usage: {input_tokens:,} input, {output_tokens:,} output
</session_metrics>

<conversation_sample>
{conversation_sample}
</conversation_sample>

<guidelines>
SUMMARY (2-3 sentences):
- What was the primary goal/task?
- Was it accomplished?

OUTCOME (one of):
- "success": Task completed successfully
- "partial": Some progress but incomplete
- "abandoned": User gave up or switched tasks
- "error": Blocked by errors/issues

WHAT_WENT_WELL (2-4 bullets):
- Effective tool usage patterns
- Good problem decomposition
- Efficient information gathering

AREAS_TO_IMPROVE (2-4 bullets):
- Inefficient patterns observed
- Missed opportunities
- Better approaches available

TIPS_FOR_FUTURE (2-3 actionable items):
- Specific, actionable advice
- Based on this session's patterns
- Help avoid similar issues

TAGS (3-5 keywords):
- Task type (debugging, feature, refactor, docs)
- Technologies mentioned
- Patterns observed (analysis-paralysis, iterative, exploratory)
</guidelines>

Respond with JSON only (no markdown, no explanation):
{{
  "summary": "...",
  "outcome": "success|partial|abandoned|error",
  "what_went_well": ["...", "..."],
  "areas_to_improve": ["...", "..."],
  "tips_for_future": ["...", "..."],
  "tags": ["...", "..."]
}}"""


# ============================================================================
# Session Data Extraction
# ============================================================================


class SessionDataExtractor:
    """Extracts metrics and context from session data."""

    def __init__(self, config: SessionLearningConfig):
        self.config = config

    def extract_metrics(
        self, session_dir: Path, metadata: dict
    ) -> SessionMetrics | None:
        """Extract metrics from session events."""
        events_path = session_dir / "events.jsonl"
        if not events_path.exists():
            return None

        # Initialize counters
        tool_usage: dict[str, int] = {}
        files_read: set[str] = set()
        files_modified: set[str] = set()
        errors = 0
        llm_requests = 0
        input_tokens = 0
        output_tokens = 0
        model_used = metadata.get("model")
        first_ts = None
        last_ts = None

        # Process events with limit
        event_count = 0
        try:
            with open(events_path, "r") as f:
                for line in f:
                    if event_count >= self.config.max_events_to_process:
                        break
                    event_count += 1

                    if not line.strip():
                        continue

                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Track timestamps
                    ts = event.get("ts")
                    if ts:
                        if first_ts is None:
                            first_ts = ts
                        last_ts = ts

                    event_type = event.get("event", "")
                    data = event.get("data", {})

                    # Track tool usage
                    if event_type == "tool:post":
                        tool_name = data.get("tool_name", "unknown")
                        tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1

                        # Track file operations
                        tool_input = data.get("tool_input", {})
                        if isinstance(tool_input, dict):
                            file_path = tool_input.get("file_path", "")
                            if file_path:
                                if tool_name == "read_file":
                                    files_read.add(self._sanitize_path(file_path))
                                elif tool_name in ("write_file", "edit_file"):
                                    files_modified.add(self._sanitize_path(file_path))

                    # Track LLM usage
                    elif event_type == "llm:response":
                        llm_requests += 1
                        usage = data.get("usage", {})
                        input_tokens += usage.get("input", 0)
                        output_tokens += usage.get("output", 0)
                        if not model_used:
                            model_used = data.get("model")

                    # Track errors
                    elif event_type in ("tool:error", "llm:error"):
                        errors += 1
                    elif event.get("lvl") == "ERROR":
                        errors += 1

        except OSError as e:
            logger.warning(f"Failed to read events file: {e}")
            return None

        # Calculate duration
        duration = 0.0
        if first_ts and last_ts:
            try:
                start = datetime.fromisoformat(first_ts.replace("Z", "+00:00"))
                end = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
                duration = (end - start).total_seconds()
            except (ValueError, TypeError):
                pass

        return SessionMetrics(
            session_id=metadata.get("session_id", "unknown"),
            duration_seconds=duration,
            turn_count=metadata.get("turn_count", 0),
            tool_usage=tool_usage,
            files_read=list(files_read),
            files_modified=list(files_modified),
            errors_encountered=errors,
            llm_requests=llm_requests,
            total_input_tokens=input_tokens,
            total_output_tokens=output_tokens,
            model_used=model_used,
            started_at=first_ts,
            ended_at=last_ts,
        )

    def extract_conversation_sample(
        self, session_dir: Path, max_chars: int = 8000
    ) -> str:
        """Extract representative conversation sample for analysis."""
        transcript_path = session_dir / "transcript.jsonl"

        # Fallback to events if no transcript
        if not transcript_path.exists():
            return self._extract_from_events(session_dir, max_chars)

        messages = []
        try:
            with open(transcript_path, "r") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        msg = json.loads(line)
                        role = msg.get("role")
                        content = msg.get("content", "")
                        if role in ("user", "assistant") and content:
                            messages.append((role, self._extract_text(content)))
                    except json.JSONDecodeError:
                        continue
        except OSError:
            return self._extract_from_events(session_dir, max_chars)

        if not messages:
            return "[No conversation content available]"

        return self._format_conversation_sample(messages, max_chars)

    def _extract_from_events(self, session_dir: Path, max_chars: int) -> str:
        """Extract conversation from events.jsonl as fallback."""
        events_path = session_dir / "events.jsonl"
        if not events_path.exists():
            return "[No session data available]"

        messages = []
        try:
            with open(events_path, "r") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        event = json.loads(line)
                        if event.get("event") == "prompt:complete":
                            data = event.get("data", {})
                            prompt = data.get("prompt", "")
                            response = data.get("response", "")
                            if prompt:
                                messages.append(("user", str(prompt)[:500]))
                            if response:
                                messages.append(("assistant", str(response)[:500]))
                    except json.JSONDecodeError:
                        continue
        except OSError:
            return "[Failed to read session data]"

        return self._format_conversation_sample(messages, max_chars)

    def _format_conversation_sample(
        self, messages: list[tuple[str, str]], max_chars: int
    ) -> str:
        """Format messages into a representative sample."""
        if not messages:
            return "[No messages]"

        n = len(messages)
        parts = []
        chars_used = 0
        char_budget = max_chars

        # Opening (first 2-3 exchanges)
        parts.append("=== Opening ===")
        for role, content in messages[: min(4, n)]:
            truncated = self._truncate(content, min(400, char_budget // 4))
            parts.append(f"[{role}]: {truncated}")
            chars_used += len(truncated)

        # Sample from middle if long
        if n > 10:
            parts.append("\n=== Middle (sampled) ===")
            mid_budget = (char_budget - chars_used) // 3
            indices = [n // 4, n // 2, 3 * n // 4]
            for i in indices:
                if 4 <= i < n - 4:
                    role, content = messages[i]
                    truncated = self._truncate(content, min(300, mid_budget // 3))
                    parts.append(f"[{role}]: {truncated}")

        # Recent (last 3-4 exchanges)
        if n > 4:
            parts.append("\n=== Recent ===")
            for role, content in messages[-min(6, n - 4) :]:
                truncated = self._truncate(content, min(400, char_budget // 4))
                parts.append(f"[{role}]: {truncated}")

        parts.append(f"\n[Total: {n} messages]")
        return "\n".join(parts)

    def _extract_text(self, content: Any) -> str:
        """Extract text from various content formats."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            texts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        texts.append(item.get("text", ""))
                elif isinstance(item, str):
                    texts.append(item)
            return " ".join(texts)
        return str(content)

    def _truncate(self, text: str, max_len: int) -> str:
        """Truncate text at word boundary."""
        if len(text) <= max_len:
            return text
        truncated = text[:max_len]
        last_space = truncated.rfind(" ")
        if last_space > max_len * 0.7:
            truncated = truncated[:last_space]
        return truncated + "..."

    def _sanitize_path(self, path: str) -> str:
        """Sanitize file path based on privacy settings."""
        if not self.config.privacy.include_file_paths:
            # Return just filename
            return Path(path).name
        # Collapse home directory
        home = str(Path.home())
        if path.startswith(home):
            return "~" + path[len(home) :]
        return path


# ============================================================================
# Insights Generator
# ============================================================================


class InsightsGenerator:
    """Generates insights using LLM analysis."""

    def __init__(self, coordinator: Any, config: SessionLearningConfig):
        self.coordinator = coordinator
        self.config = config

    async def generate_insights(
        self, metrics: SessionMetrics, conversation_sample: str
    ) -> SessionInsights | None:
        """Generate insights from session metrics and conversation."""
        # Build prompt
        prompt = self._build_prompt(metrics, conversation_sample)

        # Call LLM with timeout
        try:
            response = await asyncio.wait_for(
                self._call_provider(prompt),
                timeout=self.config.analysis_timeout_seconds,
            )
        except asyncio.TimeoutError:
            logger.warning(f"Analysis timeout for session {metrics.session_id[:8]}")
            return None

        if not response:
            return None

        # Parse response
        result = self._parse_response(response)
        if not result:
            return None

        return SessionInsights(
            session_id=metrics.session_id,
            generated_at=datetime.now(UTC).isoformat(),
            metrics={
                "duration_seconds": metrics.duration_seconds,
                "turn_count": metrics.turn_count,
                "tool_usage": metrics.tool_usage,
                "files_read_count": len(metrics.files_read),
                "files_modified_count": len(metrics.files_modified),
                "errors_encountered": metrics.errors_encountered,
                "llm_requests": metrics.llm_requests,
                "total_tokens": metrics.total_input_tokens + metrics.total_output_tokens,
            },
            summary=result.get("summary", "No summary available"),
            outcome=result.get("outcome", "unknown"),
            what_went_well=result.get("what_went_well", []),
            areas_to_improve=result.get("areas_to_improve", []),
            tips_for_future=result.get("tips_for_future", []),
            tags=result.get("tags", []),
            privacy_level=self.config.privacy.level,
        )

    def _build_prompt(self, metrics: SessionMetrics, conversation_sample: str) -> str:
        """Build the analysis prompt."""
        # Format tool usage
        tool_lines = []
        for tool, count in sorted(
            metrics.tool_usage.items(), key=lambda x: -x[1]
        )[:10]:
            tool_lines.append(f"  - {tool}: {count}")
        tool_usage_formatted = "\n".join(tool_lines) or "  (no tools used)"

        # Format files section
        files_section = ""
        if self.config.privacy.include_file_paths:
            if metrics.files_modified:
                files_section += f"\nModified: {', '.join(metrics.files_modified[:10])}"
                if len(metrics.files_modified) > 10:
                    files_section += f" (+{len(metrics.files_modified) - 10} more)"

        return ANALYSIS_PROMPT.format(
            session_id=metrics.session_id[:8] + "...",
            duration_minutes=metrics.duration_seconds / 60,
            turn_count=metrics.turn_count,
            model=metrics.model_used or "unknown",
            tool_usage_formatted=tool_usage_formatted,
            files_read_count=len(metrics.files_read),
            files_modified_count=len(metrics.files_modified),
            files_section=files_section,
            errors_count=metrics.errors_encountered,
            input_tokens=metrics.total_input_tokens,
            output_tokens=metrics.total_output_tokens,
            conversation_sample=conversation_sample,
        )

    async def _call_provider(self, prompt: str) -> str | None:
        """Call the LLM provider."""
        try:
            provider = None
            providers = self.coordinator.get("providers")
            if providers:
                provider = next(iter(providers.values()), None)

            if not provider:
                logger.warning("No provider available for session learning")
                return None

            from amplifier_core import ChatRequest, Message

            request = ChatRequest(messages=[Message(role="user", content=prompt)])
            response = await provider.complete(request)

            if response and response.content:
                text_parts = []
                for block in response.content:
                    if hasattr(block, "text"):
                        text_parts.append(block.text)
                    elif hasattr(block, "content") and isinstance(block.content, str):
                        text_parts.append(block.content)
                return "".join(text_parts) if text_parts else None

        except Exception as e:
            logger.error(f"Provider call failed: {e}")

        return None

    def _parse_response(self, response: str) -> dict | None:
        """Parse JSON response from LLM."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r"\{[^{}]*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse insights response: {e}")
            return None


# ============================================================================
# Storage
# ============================================================================


@dataclass
class SessionMetricsOnly:
    """Lightweight metrics-only storage (no LLM analysis)."""

    session_id: str
    captured_at: str
    metrics: dict[str, Any]
    privacy_level: str


class InsightsStorage:
    """Handles storing and retrieving session insights."""

    def __init__(self, config: SessionLearningConfig):
        self.config = config
        self.insights_dir = Path.home() / ".amplifier" / "insights" / "sessions"
        self.metrics_dir = Path.home() / ".amplifier" / "insights" / "metrics"

    def save_metrics_only(self, metrics: SessionMetrics) -> Path | None:
        """Save metrics without LLM analysis (lightweight, cheap)."""
        try:
            self.metrics_dir.mkdir(parents=True, exist_ok=True)
            file_path = self.metrics_dir / f"{metrics.session_id}.json"

            metrics_dict = {
                "session_id": metrics.session_id,
                "captured_at": datetime.now(UTC).isoformat(),
                "metrics": {
                    "duration_seconds": metrics.duration_seconds,
                    "turn_count": metrics.turn_count,
                    "tool_usage": metrics.tool_usage,
                    "files_read_count": len(metrics.files_read),
                    "files_modified_count": len(metrics.files_modified),
                    "files_read": metrics.files_read[:20],  # Limit for storage
                    "files_modified": metrics.files_modified[:20],
                    "errors_encountered": metrics.errors_encountered,
                    "llm_requests": metrics.llm_requests,
                    "total_input_tokens": metrics.total_input_tokens,
                    "total_output_tokens": metrics.total_output_tokens,
                    "total_tokens": metrics.total_input_tokens + metrics.total_output_tokens,
                    "model_used": metrics.model_used,
                    "started_at": metrics.started_at,
                    "ended_at": metrics.ended_at,
                },
                "privacy_level": self.config.privacy.level,
                "has_llm_analysis": False,
            }

            # Atomic write
            temp_path = file_path.with_suffix(".tmp")
            temp_path.write_text(json.dumps(metrics_dict, indent=2))
            temp_path.replace(file_path)

            logger.info(f"Saved metrics for session {metrics.session_id[:8]}")
            return file_path

        except OSError as e:
            logger.error(f"Failed to save metrics: {e}")
            return None

    def save_insights(self, insights: SessionInsights) -> Path | None:
        """Save insights to file."""
        try:
            self.insights_dir.mkdir(parents=True, exist_ok=True)
            file_path = self.insights_dir / f"{insights.session_id}.json"

            # Convert to dict
            insights_dict = {
                "session_id": insights.session_id,
                "generated_at": insights.generated_at,
                "metrics": insights.metrics,
                "summary": insights.summary,
                "outcome": insights.outcome,
                "what_went_well": insights.what_went_well,
                "areas_to_improve": insights.areas_to_improve,
                "tips_for_future": insights.tips_for_future,
                "tags": insights.tags,
                "privacy_level": insights.privacy_level,
            }

            # Atomic write
            temp_path = file_path.with_suffix(".tmp")
            temp_path.write_text(json.dumps(insights_dict, indent=2))
            temp_path.replace(file_path)

            logger.info(f"Saved insights for session {insights.session_id[:8]}")
            return file_path

        except OSError as e:
            logger.error(f"Failed to save insights: {e}")
            return None

    def load_insights(self, session_id: str) -> dict | None:
        """Load insights for a session."""
        file_path = self.insights_dir / f"{session_id}.json"
        if not file_path.exists():
            return None
        try:
            return json.loads(file_path.read_text())
        except (json.JSONDecodeError, OSError):
            return None


# ============================================================================
# Main Hook Handler
# ============================================================================


class SessionLearningHook:
    """Main hook handler for session learning."""

    def __init__(self, coordinator: Any, config: SessionLearningConfig):
        self.coordinator = coordinator
        self.config = config
        self.extractor = SessionDataExtractor(config)
        self.generator = InsightsGenerator(coordinator, config)
        self.storage = InsightsStorage(config)
        self._active_tasks: set[asyncio.Task] = set()

    async def on_session_end(self, event: str, data: dict[str, Any]) -> HookResult:
        """Handle session end event - trigger learning analysis."""
        session_id = data.get("session_id")
        if not session_id:
            return HookResult(action="continue")

        # Find session directory
        session_dir = self._get_session_dir(session_id)
        if not session_dir or not session_dir.exists():
            logger.debug(f"Session directory not found for {session_id[:8]}")
            return HookResult(action="continue")

        # Load metadata
        metadata = self._load_metadata(session_dir)

        # Check minimum thresholds
        turn_count = metadata.get("turn_count", 0)
        if turn_count < self.config.min_turns_for_analysis:
            logger.debug(
                f"Session {session_id[:8]} has only {turn_count} turns, skipping analysis"
            )
            return HookResult(action="continue")

        # Run analysis
        if self.config.run_in_background:
            # Non-blocking background analysis
            task = asyncio.create_task(
                self._analyze_session_safe(session_id, session_dir, metadata)
            )
            self._active_tasks.add(task)
            task.add_done_callback(self._active_tasks.discard)
            logger.debug(f"Started background analysis for session {session_id[:8]}")
        else:
            # Blocking analysis
            await self._analyze_session_safe(session_id, session_dir, metadata)

        return HookResult(action="continue")

    async def _analyze_session_safe(
        self, session_id: str, session_dir: Path, metadata: dict
    ) -> None:
        """Analyze session with error handling."""
        try:
            await self._analyze_session(session_id, session_dir, metadata)
        except asyncio.CancelledError:
            logger.debug(f"Analysis cancelled for session {session_id[:8]}")
        except Exception as e:
            logger.error(f"Analysis failed for session {session_id[:8]}: {e}")

    async def _analyze_session(
        self, session_id: str, session_dir: Path, metadata: dict
    ) -> None:
        """Perform session analysis with tiered capture."""
        # Extract metrics
        metrics = self.extractor.extract_metrics(session_dir, metadata)
        if not metrics:
            logger.debug(f"Could not extract metrics for session {session_id[:8]}")
            return

        # === TIER 1: Always save metrics (cheap) ===
        if self.config.always_save_metrics:
            # Check minimum thresholds for metrics
            if (
                metrics.turn_count >= self.config.min_turns_for_metrics
                and metrics.duration_seconds >= self.config.min_duration_for_metrics
            ):
                self.storage.save_metrics_only(metrics)
                logger.debug(f"Saved metrics for session {session_id[:8]}")

        # === TIER 2: LLM analysis (costs tokens) ===
        should_run_llm = False

        if self.config.llm_analysis_mode == "automatic":
            # Run on all sessions meeting basic thresholds
            should_run_llm = (
                metrics.turn_count >= self.config.min_turns_for_analysis
                and metrics.duration_seconds >= self.config.min_duration_seconds
            )
        elif self.config.llm_analysis_mode == "threshold":
            # Run only on substantive sessions
            should_run_llm = (
                metrics.turn_count >= self.config.min_turns_for_llm_analysis
                and metrics.duration_seconds >= self.config.min_duration_for_llm_analysis
            )
        # "on_demand" mode: never auto-run LLM analysis

        if not should_run_llm:
            logger.debug(
                f"Skipping LLM analysis for session {session_id[:8]} "
                f"(mode={self.config.llm_analysis_mode}, "
                f"turns={metrics.turn_count}, duration={metrics.duration_seconds}s)"
            )
            return

        # Extract conversation sample
        conversation_sample = self.extractor.extract_conversation_sample(session_dir)

        # Generate insights
        insights = await self.generator.generate_insights(metrics, conversation_sample)
        if not insights:
            logger.debug(f"Could not generate insights for session {session_id[:8]}")
            return

        # Store full insights (overwrites metrics-only if exists)
        self.storage.save_insights(insights)

        # Emit event for other hooks/tools
        await self.coordinator.hooks.emit(
            "session-learning:complete",
            {
                "session_id": session_id,
                "outcome": insights.outcome,
                "tags": insights.tags,
            },
        )

    def _get_session_dir(self, session_id: str) -> Path | None:
        """Find session directory."""
        if hasattr(self.coordinator, "session_dir"):
            return Path(self.coordinator.session_dir)

        home = Path.home()

        # Check projects structure
        projects_dir = home / ".amplifier" / "projects"
        if projects_dir.exists():
            for project_dir in projects_dir.iterdir():
                if project_dir.is_dir():
                    session_path = project_dir / "sessions" / session_id
                    if session_path.exists():
                        return session_path

        # Legacy location
        legacy_path = home / ".amplifier" / "sessions" / session_id
        if legacy_path.exists():
            return legacy_path

        return None

    def _load_metadata(self, session_dir: Path) -> dict:
        """Load session metadata."""
        metadata_path = session_dir / "metadata.json"
        if metadata_path.exists():
            try:
                return json.loads(metadata_path.read_text())
            except (json.JSONDecodeError, OSError):
                pass
        return {}


# ============================================================================
# Module Mount Point
# ============================================================================


def _load_privacy_config() -> PrivacyConfig:
    """Load privacy config from ~/.amplifier/config.yaml if present."""
    config_path = Path.home() / ".amplifier" / "config.yaml"
    if not config_path.exists():
        return PrivacyConfig()

    try:
        import yaml

        config = yaml.safe_load(config_path.read_text())
        privacy_section = config.get("privacy", {}).get("session_learning", {})
        return PrivacyConfig(
            level=privacy_section.get("level", "self"),
            include_file_paths=privacy_section.get("include_file_paths", True),
            include_code_snippets=privacy_section.get("include_code_snippets", False),
            redact_sensitive=privacy_section.get("redact_sensitive", True),
            max_context_tokens=privacy_section.get("max_context_tokens", 50000),
        )
    except Exception:
        return PrivacyConfig()


async def mount(
    coordinator: Any, config: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Mount the session learning hook module.

    Config options:
        # Metrics capture (always cheap)
        always_save_metrics: bool (default: True) - Always save metrics
        min_turns_for_metrics: int (default: 2) - Minimum turns for metrics
        min_duration_for_metrics: int (default: 30) - Minimum seconds for metrics

        # LLM analysis (costs tokens)
        llm_analysis_mode: str (default: "threshold") - "automatic", "threshold", "on_demand"
        min_turns_for_llm_analysis: int (default: 5) - Minimum turns for LLM
        min_duration_for_llm_analysis: int (default: 300) - Minimum seconds for LLM (5 min)

        # Legacy (backward compatible)
        min_turns_for_analysis: int (default: 3) - Maps to min_turns_for_metrics
        min_duration_seconds: int (default: 60) - Maps to min_duration_for_metrics

        # Processing
        max_events_to_process: int (default: 1000) - Limit for large sessions
        analysis_timeout_seconds: int (default: 60) - LLM call timeout
        run_in_background: bool (default: True) - Non-blocking analysis

        # Privacy
        privacy.level: str (default: "self") - Privacy level
        privacy.include_file_paths: bool (default: True)
        privacy.include_code_snippets: bool (default: False)
        privacy.redact_sensitive: bool (default: True)
    """
    config = config or {}

    # Load privacy config (module config overrides file config)
    privacy_config = _load_privacy_config()
    privacy_section = config.get("privacy", {})
    if privacy_section:
        privacy_config = PrivacyConfig(
            level=privacy_section.get("level", privacy_config.level),
            include_file_paths=privacy_section.get(
                "include_file_paths", privacy_config.include_file_paths
            ),
            include_code_snippets=privacy_section.get(
                "include_code_snippets", privacy_config.include_code_snippets
            ),
            redact_sensitive=privacy_section.get(
                "redact_sensitive", privacy_config.redact_sensitive
            ),
            max_context_tokens=privacy_section.get(
                "max_context_tokens", privacy_config.max_context_tokens
            ),
        )

    hook_config = SessionLearningConfig(
        # Metrics capture
        always_save_metrics=config.get("always_save_metrics", True),
        min_turns_for_metrics=config.get("min_turns_for_metrics", 2),
        min_duration_for_metrics=config.get("min_duration_for_metrics", 30),
        # LLM analysis
        llm_analysis_mode=config.get("llm_analysis_mode", "threshold"),
        min_turns_for_llm_analysis=config.get("min_turns_for_llm_analysis", 5),
        min_duration_for_llm_analysis=config.get("min_duration_for_llm_analysis", 300),
        # Legacy
        min_turns_for_analysis=config.get("min_turns_for_analysis", 3),
        min_duration_seconds=config.get("min_duration_seconds", 60),
        # Processing
        max_events_to_process=config.get("max_events_to_process", 1000),
        analysis_timeout_seconds=config.get("analysis_timeout_seconds", 60),
        run_in_background=config.get("run_in_background", True),
        privacy=privacy_config,
    )

    hook = SessionLearningHook(coordinator, hook_config)

    # Register for session end events
    # Use very low priority (high number) so we run last
    coordinator.hooks.register(
        "session:end",
        hook.on_session_end,
        priority=200,  # Run after other session hooks
        name="session-learning",
    )

    return {
        "name": "hooks-session-learning",
        "version": "0.2.0",
        "description": "Session analysis and learning insights generation",
        "config": {
            "always_save_metrics": hook_config.always_save_metrics,
            "llm_analysis_mode": hook_config.llm_analysis_mode,
            "min_turns_for_metrics": hook_config.min_turns_for_metrics,
            "min_turns_for_llm_analysis": hook_config.min_turns_for_llm_analysis,
            "run_in_background": hook_config.run_in_background,
            "privacy_level": hook_config.privacy.level,
        },
    }
