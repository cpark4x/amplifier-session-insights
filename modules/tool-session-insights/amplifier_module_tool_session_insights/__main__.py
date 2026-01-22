"""CLI entry point for session insights tool."""

import json
import sys

from . import analyze_session, find_session_dir, list_recent_sessions


def main():
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


if __name__ == "__main__":
    main()
