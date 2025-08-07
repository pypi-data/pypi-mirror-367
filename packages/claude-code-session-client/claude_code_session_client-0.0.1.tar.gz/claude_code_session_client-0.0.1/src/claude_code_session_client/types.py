"""Type definitions for Claude Code Session Client."""

# Re-export types from claude-code-sdk-python for convenience
from claude_code_sdk.types import (
    AssistantMessage,
    ClaudeCodeOptions,
    Message,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)

from ._internal.session_storage import SessionData

# Define a convenient type for conversation messages
ConversationMessage = UserMessage | AssistantMessage | SystemMessage | ResultMessage

__all__ = [
    "AssistantMessage",
    "ClaudeCodeOptions",
    "ConversationMessage",
    "Message",
    "ResultMessage",
    "SessionData",
    "SystemMessage",
    "TextBlock",
    "ToolResultBlock",
    "ToolUseBlock",
    "UserMessage",
]
