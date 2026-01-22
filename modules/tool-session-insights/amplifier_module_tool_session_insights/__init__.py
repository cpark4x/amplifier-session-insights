"""
Session Insights Tool - On-demand session analysis for Amplifier.

Provides a tool that can be invoked to analyze any session,
showing metrics, effectiveness, and tips for improvement.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = "tool-session-insights"
MODULE_VERSION = "0.2.0"


def get_tool_definitions() -> list[dict[str, Any]]:
    """Return tool definitions for this module."""
    return [
        {
            "name": "session_insights",
            "description": """Analyze a session and provide insights.

Use this tool when the user wants to:
- See how the current session is going
- Analyze a past session by ID
- Get metrics about a session (duration, tools used, etc.)
- Understand what went well and what could improve
- Get tips for improvement

Parameters:
- session_id: Optional. Analyze a specific session. If not provided, analyzes current session.
- include_tips: Include actionable tips (default: true)
- verbose: Include detailed metrics (default: false)""",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to analyze. If not provided, analyzes current session."
                    },
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


def find_session_dir(session_id: str) -> Path | None:
    """Find session directory by ID, searching all project paths."""
    amplifier_dir = Path.home() / ".amplifier"
    
    # Search patterns for session directories
    search_paths = [
        amplifier_dir / "sessions" / session_id,  # Direct path
        amplifier_dir / "projects",  # Project-based sessions
    ]
    
    # Check direct path first
    direct_path = amplifier_dir / "sessions" / session_id
    if direct_path.exists():
        return direct_path
    
    # Search in projects directory
    projects_dir = amplifier_dir / "projects"
    if projects_dir.exists():
        for project_dir in projects_dir.iterdir():
            if project_dir.is_dir():
                sessions_dir = project_dir / "sessions"
                if sessions_dir.exists():
                    # Check for exact match
                    session_path = sessions_dir / session_id
                    if session_path.exists():
                        return session_path
                    # Check for partial match (session ID prefix)
                    for entry in sessions_dir.iterdir():
                        if entry.is_dir() and entry.name.startswith(session_id):
                            return entry
    
    return None


def list_recent_sessions(limit: int = 10) -> list[dict[str, Any]]:
    """List recent sessions across all projects."""
    amplifier_dir = Path.home() / ".amplifier"
    sessions = []
    
    # Search in projects directory
    projects_dir = amplifier_dir / "projects"
    if projects_dir.exists():
        for project_dir in projects_dir.iterdir():
            if project_dir.is_dir():
                sessions_dir = project_dir / "sessions"
                if sessions_dir.exists():
                    for session_dir in sessions_dir.iterdir():
                        # Skip child sessions (contain underscore after UUID)
                        if session_dir.is_dir() and "_" not in session_dir.name:
                            metadata_file = session_dir / "metadata.json"
                            if metadata_file.exists():
                                try:
                                    with open(metadata_file) as f:
                                        metadata = json.load(f)
                                    sessions.append({
                                        "session_id": session_dir.name,
                                        "name": metadata.get("name", "unnamed"),
                                        "created": metadata.get("created", ""),
                                        "turn_count": metadata.get("turn_count", 0),
                                        "path": str(session_dir)
                                    })
                                except Exception:
                                    pass
    
    # Sort by created date (newest first)
    sessions.sort(key=lambda x: x.get("created", ""), reverse=True)
    return sessions[:limit]


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


def extract_metrics(session_dir: str) -> dict[str, Any]:
    """Extract metrics from session directory."""
    session_path = Path(session_dir)
    metrics = {
        "duration_seconds": 0,
        "turn_count": 0,
        "user_message_count": 0,
        "assistant_message_count": 0,
        "tool_usage": {},
        "files_read": [],
        "files_modified": [],
        "session_name": "unnamed",
        "model": "unknown",
        "created": None,
    }
    
    # Read metadata
    metadata_file = session_path / "metadata.json"
    if metadata_file.exists():
        try:
            with open(metadata_file) as f:
                metadata = json.load(f)
            
            metrics["session_name"] = metadata.get("name", "unnamed")
            metrics["model"] = metadata.get("model", "unknown")
            metrics["turn_count"] = metadata.get("turn_count", 0)
            
            # Calculate duration from created timestamp
            created = metadata.get("created")
            if created:
                metrics["created"] = created
                try:
                    start_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    now = datetime.now(timezone.utc)
                    metrics["duration_seconds"] = (now - start_dt).total_seconds()
                except Exception:
                    pass
        except Exception:
            pass
    
    # Read transcript for detailed metrics
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
                        elif role == "assistant":
                            metrics["assistant_message_count"] += 1
                            
                            # Extract tool usage from assistant content
                            content = entry.get("content", [])
                            if isinstance(content, list):
                                for block in content:
                                    if isinstance(block, dict) and block.get("type") == "tool_use":
                                        tool_name = block.get("name", "unknown")
                                        metrics["tool_usage"][tool_name] = metrics["tool_usage"].get(tool_name, 0) + 1
                                        
                                        # Extract file paths from tool inputs
                                        tool_input = block.get("input", {})
                                        if isinstance(tool_input, dict):
                                            # Check for file_path in various tools
                                            file_path = tool_input.get("file_path") or tool_input.get("path")
                                            if file_path and isinstance(file_path, str):
                                                if tool_name in ("read_file", "glob", "grep"):
                                                    if file_path not in metrics["files_read"]:
                                                        metrics["files_read"].append(file_path)
                                                elif tool_name in ("write_file", "edit_file"):
                                                    if file_path not in metrics["files_modified"]:
                                                        metrics["files_modified"].append(file_path)
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
    
    # Fallback: use grep-style extraction if no tool usage found
    if not metrics["tool_usage"] and transcript_file.exists():
        try:
            content = transcript_file.read_text()
            # Match "name": "tool_name" patterns
            tool_matches = re.findall(r'"name":\s*"([^"]+)"', content)
            for tool_name in tool_matches:
                # Filter out non-tool names (like model names, etc.)
                if tool_name in ("bash", "read_file", "write_file", "edit_file", 
                                 "glob", "grep", "task", "todo", "python_check",
                                 "recipes", "load_skill", "session_insights"):
                    metrics["tool_usage"][tool_name] = metrics["tool_usage"].get(tool_name, 0) + 1
        except Exception:
            pass
    
    return metrics


def generate_assessment(metrics: dict[str, Any]) -> dict[str, Any]:
    """Generate assessment of the session."""
    duration = metrics.get("duration_seconds", 0)
    turns = metrics.get("turn_count", 0) or metrics.get("user_message_count", 0)
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
    if turns > 0 and tool_calls > 0:
        tools_per_turn = tool_calls / turns
        if tools_per_turn > 3:
            tool_intensity = "high"
        elif tools_per_turn > 1:
            tool_intensity = "moderate"
        else:
            tool_intensity = "low"
    else:
        tool_intensity = "minimal"
    
    return {
        "pace": pace,
        "pace_note": pace_note,
        "tool_intensity": tool_intensity,
        "tools_per_turn": round(tool_calls / max(turns, 1), 1)
    }


def generate_tips(metrics: dict[str, Any]) -> list[str]:
    """Generate contextual tips based on session metrics."""
    tips = []
    
    duration = metrics.get("duration_seconds", 0)
    turns = metrics.get("turn_count", 0) or metrics.get("user_message_count", 0)
    tool_usage = metrics.get("tool_usage", {})
    
    # Duration-based tips
    if duration > 7200:  # 2 hours
        tips.append("Long session! Consider taking a break or summarizing progress.")
    
    # Tool usage tips
    bash_calls = tool_usage.get("bash", 0)
    if bash_calls > 20:
        tips.append(f"Heavy bash usage ({bash_calls} calls) - consider specialized tools for some tasks.")
    
    read_calls = tool_usage.get("read_file", 0)
    if read_calls > 30:
        tips.append(f"Many file reads ({read_calls}) - grep/glob might find things faster.")
    
    if not tool_usage.get("todo") and turns > 15:
        tips.append("Consider using todo tool to track progress on complex tasks.")
    
    if tool_usage.get("todo", 0) > 10:
        tips.append("Great job using todo to stay organized!")
    
    # Pace tips
    if turns > 0 and duration > 0:
        mins_per_turn = (duration / 60) / turns
        if mins_per_turn > 5:
            tips.append("Responses taking a while - try smaller, focused requests.")
    
    # Default tip
    if not tips:
        tips.append("Session looks good! Keep up the focused work.")
    
    return tips


def analyze_session(session_dir: str, include_tips: bool = True, verbose: bool = False) -> dict[str, Any]:
    """Analyze a session and return insights."""
    session_path = Path(session_dir)
    
    if not session_path.exists():
        return {"error": f"Session directory not found: {session_dir}"}
    
    # Extract metrics
    metrics = extract_metrics(session_dir)
    
    # Build insights response
    turns = metrics.get("turn_count", 0) or metrics.get("user_message_count", 0)
    tool_calls = sum(metrics.get("tool_usage", {}).values())
    
    insights = {
        "session_id": session_path.name,
        "session_name": metrics.get("session_name", "unnamed"),
        "status": "completed" if metrics.get("duration_seconds", 0) > 0 else "in_progress",
        "metrics": {
            "duration": format_duration(metrics.get("duration_seconds", 0)),
            "turns": turns,
            "total_tool_calls": tool_calls,
            "model": metrics.get("model", "unknown"),
        }
    }
    
    # Add top tools
    if metrics.get("tool_usage"):
        tool_usage = metrics["tool_usage"]
        top_tools = sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)[:7]
        insights["top_tools"] = [{"tool": t, "calls": c} for t, c in top_tools]
    
    # Add file activity
    files_read = len(metrics.get("files_read", []))
    files_modified = len(metrics.get("files_modified", []))
    if files_read > 0 or files_modified > 0:
        insights["file_activity"] = {
            "files_read": files_read,
            "files_modified": files_modified
        }
        if verbose:
            insights["file_activity"]["read_list"] = metrics.get("files_read", [])[:10]
            insights["file_activity"]["modified_list"] = metrics.get("files_modified", [])[:10]
    
    # Add assessment
    insights["assessment"] = generate_assessment(metrics)
    
    # Add tips if requested
    if include_tips:
        insights["tips"] = generate_tips(metrics)
    
    # Add verbose details
    if verbose:
        insights["raw_metrics"] = metrics
    
    return insights


async def handle_tool_call(tool_name: str, tool_input: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Handle tool invocations."""
    
    if tool_name != "session_insights":
        return {"error": f"Unknown tool: {tool_name}"}
    
    # Get session ID from input or context
    session_id = tool_input.get("session_id") or context.get("session_id")
    
    if not session_id:
        # List recent sessions if no ID provided
        recent = list_recent_sessions(5)
        return {
            "error": "No session ID provided",
            "hint": "Provide a session_id parameter or use one of these recent sessions:",
            "recent_sessions": recent
        }
    
    # Find session directory
    session_dir = find_session_dir(session_id)
    
    if not session_dir:
        recent = list_recent_sessions(5)
        return {
            "error": f"Session not found: {session_id}",
            "hint": "Try one of these recent sessions:",
            "recent_sessions": recent
        }
    
    # Run analysis
    include_tips = tool_input.get("include_tips", True)
    verbose = tool_input.get("verbose", False)
    
    return analyze_session(str(session_dir), include_tips, verbose)


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


# CLI entry point for standalone testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        session_id = sys.argv[1]
        session_dir = find_session_dir(session_id)
        if session_dir:
            insights = analyze_session(str(session_dir))
            print(json.dumps(insights, indent=2))
        else:
            print(f"Session not found: {session_id}")
            print("\nRecent sessions:")
            for s in list_recent_sessions():
                print(f"  {s['session_id'][:8]}... | {s['turn_count']} turns | {s['name']}")
    else:
        print("Usage: python -m amplifier_module_tool_session_insights <session_id>")
        print("\nRecent sessions:")
        for s in list_recent_sessions():
            print(f"  {s['session_id'][:8]}... | {s['turn_count']} turns | {s['name']}")
