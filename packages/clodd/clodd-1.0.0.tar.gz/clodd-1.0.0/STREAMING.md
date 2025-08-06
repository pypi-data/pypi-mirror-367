# 🚀 Claude Code Log Streaming

Stream Claude Code session logs in real-time via WebSocket for building dashboards, monitoring tools, and session persistence features.

## Features

- **Real-time streaming** - Watch Claude Code logs as they're written
- **Session management** - Track conversation threads and metadata  
- **WebSocket API** - Easy integration with web dashboards
- **Pydantic models** - Type-safe log parsing and validation
- **CLI tools** - Built-in commands for analysis and streaming

## Quick Start

### 1. Start the Streaming Server

```bash
# Start WebSocket server on localhost:8765
clod logs stream

# Custom host/port
clod logs stream --host 0.0.0.0 --port 9000

# Debug mode
clod logs stream --debug
```

### 2. Connect with Python Client

```bash
# Connect to streaming server
clod logs client

# Custom server URI
clod logs client ws://localhost:9000
```

### 3. Open Web Dashboard

Open `examples/web_dashboard.html` in your browser and connect to `ws://localhost:8765`.

## Architecture

### JSONL Log Format

Claude Code stores session logs as JSONL files in `~/.claude/projects/`. Each line is a JSON object representing a log entry:

```json
{
  "uuid": "2a7cf41c-2247-4974-ae25-26def3b51a6c",
  "sessionId": "00eefbaa-c1c4-470e-a45c-31d2c0b8300f", 
  "timestamp": "2025-07-26T01:18:02.880Z",
  "type": "user",
  "message": {
    "role": "user",
    "content": "can u confirm if we're in the venv rn"
  },
  "cwd": "/Users/me/code/ai/clod",
  "version": "1.0.61"
}
```

### Streaming Process

1. **File Watching** - Uses `watchdog` to monitor `~/.claude/projects/` for changes
2. **JSONL Parsing** - Parses new entries with Pydantic models
3. **WebSocket Broadcasting** - Streams validated entries to connected clients
4. **Session Tracking** - Maintains conversation threads and metadata

### WebSocket API

**Message Types:**

```typescript
// Server -> Client
{
  "type": "log_entry",
  "data": ClaudeLogEntry  // New log entry
}

{
  "type": "history", 
  "data": ClaudeLogEntry[]  // Historical entries
}

// Client -> Server  
{
  "type": "ping"  // Heartbeat
}

{
  "type": "request_history",
  "limit": 50  // Request recent entries
}
```

## CLI Commands

### Analysis Commands

```bash
# Show recent sessions
clod logs recent -n 10

# Detailed view with conversation previews
clod logs recent --detailed

# Overall statistics
clod logs stats
```

### Streaming Commands

```bash
# Start streaming server
clod logs stream --host localhost --port 8765

# Connect client to server
clod logs client ws://localhost:8765
```

## Programming API

### Parse Existing Sessions

```python
from clod.log_parser import get_recent_sessions, parse_jsonl_file
from pathlib import Path

# Get recent sessions
sessions = get_recent_sessions(limit=10)

# Parse specific log file
session = parse_jsonl_file(Path("~/.claude/projects/.../session.jsonl"))

# Analyze conversation
for entry in session.get_conversation_thread():
    print(f"{entry.message.role}: {entry.message.content}")
```

### Export to SDK Format

```python
from clod.log_parser import export_session_to_sdk_format

# Convert to claude-code-sdk compatible format
sdk_messages = export_session_to_sdk_format(session)

# Use with claude-code-sdk
from claude_code_sdk import query

for message in sdk_messages:
    print(f"{message['role']}: {message['content']}")
```

### Custom Streaming Client

```python
import asyncio
import json
import websockets
from clod.models.claude_log import ClaudeLogEntry

async def stream_logs():
    async with websockets.connect("ws://localhost:8765") as websocket:
        async for message in websocket:
            data = json.loads(message)
            
            if data["type"] == "log_entry":
                entry = ClaudeLogEntry(**data["data"])
                print(f"New entry: {entry.type} - {entry.message}")

asyncio.run(stream_logs())
```

## Use Cases

### 1. Session Persistence

Build a system to save and restore Claude Code conversations:

```python
# Save conversations to database
for session in get_recent_sessions():
    save_to_database(session.session_id, session.get_conversation_thread())

# Restore conversation
messages = load_from_database(session_id)
sdk_messages = convert_to_sdk_format(messages)
```

### 2. Usage Analytics

Monitor tool usage and conversation patterns:

```python
# Analyze tool usage
tool_stats = {}
for session in get_recent_sessions(limit=100):
    for entry in session.entries:
        if entry.message and isinstance(entry.message.content, list):
            for block in entry.message.content:
                if hasattr(block, 'name'):
                    tool_stats[block.name] = tool_stats.get(block.name, 0) + 1

print("Most used tools:", sorted(tool_stats.items(), key=lambda x: x[1], reverse=True))
```

### 3. Real-time Dashboard

Build a web dashboard showing live Claude Code activity:

- **Session monitoring** - Track active conversations
- **Tool usage stats** - Monitor what tools are being used
- **Error tracking** - Alert on failures or issues
- **Performance metrics** - Analyze response times and token usage

### 4. Team Collaboration

Share Claude Code sessions across team members:

- **Session sharing** - Export/import conversation threads
- **Code review** - Review Claude's code suggestions
- **Knowledge base** - Build searchable archive of solutions

## Implementation Details

### File Watching Strategy

The streaming server uses several approaches for reliable JSONL streaming:

1. **Position Tracking** - Remembers file positions to avoid re-reading
2. **Tail Behavior** - Only processes new entries appended to files
3. **Graceful Errors** - Continues on parse failures, logging warnings
4. **Session Correlation** - Groups entries by `sessionId` for threading

### Performance Considerations

- **Efficient Parsing** - Only parses new entries, not entire files
- **Memory Management** - Limits historical entry retention
- **Connection Handling** - Supports multiple concurrent WebSocket clients
- **Error Resilience** - Handles malformed entries gracefully

### Compatibility

The Pydantic models handle various Claude Code log formats:

- ✅ **Core Messages** - User/assistant/system entries
- ✅ **Tool Execution** - Tool use and result blocks  
- ✅ **Session Metadata** - Timestamps, UUIDs, environment context
- ✅ **Summary Entries** - Session summaries and navigation
- ⚠️ **Edge Cases** - Some complex tool results need refinement

## Troubleshooting

### Common Issues

**Server won't start:**
```bash
# Check if port is in use
lsof -i :8765

# Try different port
clod logs stream --port 9000
```

**No log files found:**
```bash
# Check Claude Code projects directory
ls ~/.claude/projects/

# Verify recent activity
clod logs recent
```

**Parse errors:**
```bash
# Enable debug mode to see parsing issues
clod logs stream --debug
```

**WebSocket connection fails:**
```bash
# Check firewall settings
# Ensure server is running
# Try localhost instead of 0.0.0.0
```

### Advanced Configuration

Set custom projects directory:
```python
from clod.log_parser import find_log_files
from pathlib import Path

# Custom directory
custom_projects = Path("/custom/claude/projects")
log_files = find_log_files(custom_projects)
```

## Future Enhancements

- **Filtering** - Stream only specific session types or tools
- **Authentication** - Secure WebSocket connections
- **Persistence** - Built-in database storage for sessions
- **REST API** - HTTP endpoints for session management
- **Integrations** - Slack/Discord bots for team notifications