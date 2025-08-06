#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

import json
import sys


def main() -> None:
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        # Example: Output JSON with systemMessage for testing
        response = {
            "systemMessage": "🔧 Test hook executed - this is a system message for warnings/context",
            "continue": True
        }

        print(json.dumps(response))
        sys.exit(0)

    except Exception as e:
        # Fallback system message on error
        error_response = {
            "systemMessage": f"⚠️ Hook error: {e!s}",
            "continue": True
        }
        print(json.dumps(error_response))
        sys.exit(1)

if __name__ == "__main__":
    main()
