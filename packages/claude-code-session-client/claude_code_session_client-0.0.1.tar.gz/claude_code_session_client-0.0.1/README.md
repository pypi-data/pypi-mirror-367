# Claude Code Session Client

A session-persistent client wrapper for the [Claude Code SDK Python](https://github.com/anthropics/claude-code-sdk-python) that provides automatic conversation persistence and session resumption capabilities.

## Features

- **Automatic Session Persistence**: Conversations are automatically saved to local storage
- **Session Resumption**: Resume previous conversations using session IDs
- **Context Retention**: Maintain conversation context across client restarts
- **Multi-turn Conversations**: Seamlessly handle complex multi-turn interactions
- **Storage Management**: Organized session storage with metadata tracking

## Installation

```bash
pip install claude-code-session-client
```

## Quick Start

```python
import trio
from pathlib import Path
from claude_code_session_client import SessionPersistentClient
from claude_code_sdk import ClaudeCodeOptions

async def main():
    storage_path = Path("./sessions")
    
    async with SessionPersistentClient(
        options=ClaudeCodeOptions(),
        storage_path=storage_path
    ) as client:
        # Start conversation
        await client.query("Hello! What can you help me with?")
        
        async for message in client.receive_response():
            # Handle responses
            print(message)

if __name__ == "__main__":
    trio.run(main)
```

## Session Resumption

```python
# Resume a previous session
session_id = "your-session-id"
await client.start_or_resume_session(session_id)
```

## Requirements

- Python 3.10+
- claude-code-sdk-python
- trio

## License

MIT License