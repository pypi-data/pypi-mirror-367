#!/usr/bin/env python3
"""
Simple example using SessionPersistentClient.

This demonstrates basic usage of the session-persistent client for
automatic conversation persistence.
"""

import trio
from pathlib import Path

from claude_code_session_client import SessionPersistentClient
from claude_code_sdk import ClaudeCodeOptions
from claude_code_sdk.types import AssistantMessage, TextBlock


async def simple_demo():
    """Demonstrate simple session persistence."""
    print("=== Simple Session Persistence Demo ===")
    
    storage_path = Path("./simple_sessions")
    
    async with SessionPersistentClient(
        options=ClaudeCodeOptions(),
        storage_path=storage_path
    ) as client:
        
        # Send a message
        print("\n💬 User: Hello! Can you help me understand Python decorators?")
        await client.query("Hello! Can you help me understand Python decorators?")
        
        # Receive and print response
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")
        
        # Show session info
        session_id = client.get_current_session_id()
        session_data = await client.load_session(session_id)
        
        print(f"\n📋 Session Info:")
        print(f"   ID: {session_id}")
        print(f"   Messages: {len(session_data.conversation_history) if session_data else 'Unknown'}")
        print(f"   Saved to: {storage_path.absolute()}")


async def main():
    """Run the simple demo."""
    await simple_demo()
    
    print("\n✅ Session automatically saved!")


if __name__ == "__main__":
    trio.run(main)