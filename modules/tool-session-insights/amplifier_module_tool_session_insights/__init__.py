"""
Session Insights Tool - On-demand session analysis for Amplifier.

Provides a tool that can be invoked to analyze the current session,
showing metrics, effectiveness, and tips for improvement.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

# Import from the hooks module for shared functionality
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "hooks-session-learning"))

try:
    from amplifier_module_hooks_session_learning import extract_metrics
except ImportError:
    extract_metrics = None


MODULE_NAME = "tool-session-insights"
MODULE_VERSION = "0.1.0"


def get_tool_definitions() -> list[dict[str, Any]]:
    """Return tool definitions for this module."""
    return [
        {
            "name": "session_insights",
            "description": """Analyze the current session and provide insights.

Use this tool when the user wants to:
- See how the current session is going
- Get metrics about the session (duration, tools used, etc.)
- Understand what's going well and what could improve
- Get tips for the remainder of the session

This provides on-demand analysis without waiting for session end.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "include_tips": {
                        "type": "boolean",
                        "description": "Include tips for improvement (default: true)",
                        "default": True
                    },
                    "verbose": {
                        "type": "boolean", 
                        "description": "Include detailed metrics (default: false)",
                        "default": False
                    }
                },
                "required": []
            }
        }
    ]


def format_duration(seconds: float) -> str:
    """Format duration in human-readable form."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


def analyze_current_session(session_dir: str, include_tips: bool = True, verbose: bool = False) -> dict[str, Any]:
    """Analyze the current session and return insights."""
    
    session_path = Path(session_dir)
    
    if not session_path.exists():
        return {"error": f"Session directory not found: {session_dir}"}
    
    # Extract metrics
    if extract_metrics:
        metrics = extract_metrics(session_dir)
    else:
        # Fallback: basic metrics extraction
        metrics = extract_basic_metrics(session_dir)
    
    # Build insights response
    insights = {
        "session_id": session_path.name,
        "status": "in_progress",
        "metrics": {
            "duration": format_duration(metrics.get("duration_seconds", 0)),
            "duration_seconds": metrics.get("duration_seconds", 0),
            "turns": metrics.get("turn_count", 0),
            "user_messages": metrics.get("user_message_count", 0),
            "assistant_messages": metrics.get("assistant_message_count", 0),
        }
    }
    
    # Add tool usage if available
    if metrics.get("tool_usage"):
        tool_usage = metrics["tool_usage"]
        top_tools = sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        insights["top_tools"] = [{"tool": t, "calls": c} for t, c in top_tools]
        insights["metrics"]["total_tool_calls"] = sum(tool_usage.values())
    
    # Add file activity if available
    if metrics.get("files_read") or metrics.get("files_modified"):
        insights["file_activity"] = {
            "files_read": len(metrics.get("files_read", [])),
            "files_modified": len(metrics.get("files_modified", []))
        }
        if verbose:
            insights["file_activity"]["read_list"] = metrics.get("files_read", [])[:10]
            insights["file_activity"]["modified_list"] = metrics.get("files_modified", [])[:10]
    
    # Add tokens if available
    if metrics.get("total_tokens"):
        insights["metrics"]["tokens"] = metrics["total_tokens"]
    
    # Add verbose details
    if verbose:
        insights["detailed_metrics"] = metrics
    
    # Generate quick assessment
    insights["assessment"] = generate_quick_assessment(metrics)
    
    # Add tips if requested
    if include_tips:
        insights["tips"] = generate_session_tips(metrics)
    
    return insights


def extract_basic_metrics(session_dir: str) -> dict[str, Any]:
    """Basic metrics extraction fallback."""
    session_path = Path(session_dir)
    metrics = {
        "duration_seconds": 0,
        "turn_count": 0,
        "user_message_count": 0,
        "assistant_message_count": 0,
        "tool_usage": {},
        "files_read": [],
        "files_modified": []
    }
    
    # Read metadata for timing
    metadata_file = session_path / "metadata.json"
    if metadata_file.exists():
        try:
            with open(metadata_file) as f:
                metadata = json.load(f)
            start_time = metadata.get("created_at") or metadata.get("start_time")
            if start_time:
                start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                metrics["duration_seconds"] = (datetime.now(start_dt.tzinfo) - start_dt).total_seconds()
        except Exception:
            pass
    
    # Read transcript for counts
    transcript_file = session_path / "transcript.jsonl"
    if transcript_file.exists():
        try:
            with open(transcript_file) as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                        role = entry.get("role")
                        if role == "user":
                            metrics["user_message_count"] += 1
                            metrics["turn_count"] += 1
                        elif role == "assistant":
                            metrics["assistant_message_count"] += 1
                            
                            # Count tool usage
                            content = entry.get("content", [])
                            if isinstance(content, list):
                                for block in content:
                                    if isinstance(block, dict) and block.get("type") == "tool_use":
                                        tool_name = block.get("name", "unknown")
                                        metrics["tool_usage"][tool_name] = metrics["tool_usage"].get(tool_name, 0) + 1
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
    
    return metrics


def generate_quick_assessment(metrics: dict[str, Any]) -> dict[str, Any]:
    """Generate a quick assessment of the session."""
    duration = metrics.get("duration_seconds", 0)
    turns = metrics.get("turn_count", 0)
    tool_calls = sum(metrics.get("tool_usage", {}).values())
    
    # Calculate pace
    if duration > 0 and turns > 0:
        mins_per_turn = (duration / 60) / turns
        if mins_per_turn < 1:
            pace = "fast"
            pace_note = "Quick back-and-forth exchanges"
        elif mins_per_turn < 3:
            pace = "moderate"
            pace_note = "Balanced conversation pace"
        else:
            pace = "deliberate"
            pace_note = "Taking time on each exchange"
    else:
        pace = "unknown"
        pace_note = "Not enough data"
    
    # Calculate tool intensity
    if turns > 0:
        tools_per_turn = tool_calls / turns
        if tools_per_turn > 3:
            tool_intensity = "high"
        elif tools_per_turn > 1:
            tool_intensity = "moderate"
        else:
            tool_intensity = "low"
    else:
        tool_intensity = "unknown"
    
    return {
        "pace": pace,
        "pace_note": pace_note,
        "tool_intensity": tool_intensity,
        "tools_per_turn": round(tool_calls / max(turns, 1), 1)
    }


def generate_session_tips(metrics: dict[str, Any]) -> list[str]:
    """Generate contextual tips based on session metrics."""
    tips = []
    
    duration = metrics.get("duration_seconds", 0)
    turns = metrics.get("turn_count", 0)
    tool_usage = metrics.get("tool_usage", {})
    
    # Duration-based tips
    if duration > 7200:  # 2 hours
        tips.append("Long session! Consider taking a break or summarizing progress so far.")
    
    # Tool usage tips
    if tool_usage.get("bash", 0) > 20:
        tips.append("Heavy bash usage - consider if there's a more direct approach for some tasks.")
    
    if tool_usage.get("read_file", 0) > 30:
        tips.append("Lots of file reads - you might benefit from grep/glob to find what you need faster.")
    
    if not tool_usage.get("todo") and turns > 15:
        tips.append("Consider using the todo tool to track progress on complex tasks.")
    
    # Pace tips
    if turns > 0 and duration > 0:
        mins_per_turn = (duration / 60) / turns
        if mins_per_turn > 5:
            tips.append("Responses are taking a while - try breaking complex requests into smaller steps.")
    
    # Default tip if none generated
    if not tips:
        tips.append("Session looks good! Keep up the focused work.")
    
    return tips


async def handle_tool_call(tool_name: str, tool_input: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Handle tool invocations."""
    
    if tool_name != "session_insights":
        return {"error": f"Unknown tool: {tool_name}"}
    
    # Get session directory from context
    session_id = context.get("session_id")
    if not session_id:
        return {"error": "No session ID available in context"}
    
    # Determine session directory
    sessions_dir = Path.home() / ".amplifier" / "sessions"
    session_dir = sessions_dir / session_id
    
    if not session_dir.exists():
        return {"error": f"Session directory not found: {session_dir}"}
    
    # Run analysis
    include_tips = tool_input.get("include_tips", True)
    verbose = tool_input.get("verbose", False)
    
    insights = analyze_current_session(str(session_dir), include_tips, verbose)
    
    return insights


def mount(coordinator, config: dict[str, Any] | None = None):
    """Mount the tool module to the coordinator."""
    config = config or {}
    
    # Register tool definitions
    tools = get_tool_definitions()
    for tool_def in tools:
        coordinator.register_tool(tool_def, handle_tool_call)
    
    return {
        "name": MODULE_NAME,
        "version": MODULE_VERSION,
        "tools": [t["name"] for t in tools]
    }
