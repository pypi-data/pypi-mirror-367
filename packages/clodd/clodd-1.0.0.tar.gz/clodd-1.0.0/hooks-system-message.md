# Claude Code Hooks: systemMessage Field

Added in v1.0.64, the `systemMessage` field allows hooks to display contextual information to users.

## Usage

Hooks can output JSON with a `systemMessage` field:

```json
{
  "systemMessage": "⚠️ Lint failed but continuing",
  "continue": true
}
```

## Use Cases

- Build/test status notifications
- Warning messages for development issues
- Workflow reminders and context
- Tool execution feedback

The message appears in the Claude Code interface when the hook executes, providing real-time feedback without interrupting the conversation flow.