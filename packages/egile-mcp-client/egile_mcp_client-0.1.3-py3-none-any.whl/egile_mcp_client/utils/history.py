"""Conversation history management."""

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..agents.base import Message


@dataclass
class Conversation:
    """A conversation session."""

    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[Message]
    server_name: Optional[str] = None
    agent_provider: Optional[str] = None


class HistoryManager:
    """Manages conversation history storage and retrieval."""

    def __init__(
        self,
        storage_type: str = "file",
        file_path: str = "data/conversation_history.json",
        max_conversations: int = 100,
    ):
        self.storage_type = storage_type
        self.file_path = Path(file_path)
        self.max_conversations = max_conversations
        self.conversations: Dict[str, Conversation] = {}

        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing conversations
        self.load_conversations()

    def generate_conversation_id(self) -> str:
        """Generate a unique conversation ID."""
        return (
            f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.conversations)}"
        )

    def create_conversation(
        self,
        title: str,
        server_name: Optional[str] = None,
        agent_provider: Optional[str] = None,
    ) -> str:
        """Create a new conversation."""
        conv_id = self.generate_conversation_id()
        now = datetime.now()

        conversation = Conversation(
            id=conv_id,
            title=title,
            created_at=now,
            updated_at=now,
            messages=[],
            server_name=server_name,
            agent_provider=agent_provider,
        )

        self.conversations[conv_id] = conversation
        self.save_conversations()
        return conv_id

    def add_message(self, conversation_id: str, message: Message) -> None:
        """Add a message to a conversation."""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")

        self.conversations[conversation_id].messages.append(message)
        self.conversations[conversation_id].updated_at = datetime.now()
        self.save_conversations()

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return self.conversations.get(conversation_id)

    def get_conversation_messages(self, conversation_id: str) -> List[Message]:
        """Get messages from a conversation."""
        conversation = self.get_conversation(conversation_id)
        return conversation.messages if conversation else []

    def list_conversations(self, limit: int = 50) -> List[Conversation]:
        """List conversations sorted by update time."""
        conversations = list(self.conversations.values())
        conversations.sort(key=lambda c: c.updated_at, reverse=True)
        return conversations[:limit]

    def update_conversation_title(self, conversation_id: str, title: str) -> None:
        """Update conversation title."""
        if conversation_id in self.conversations:
            self.conversations[conversation_id].title = title
            self.conversations[conversation_id].updated_at = datetime.now()
            self.save_conversations()

    def delete_conversation(self, conversation_id: str) -> None:
        """Delete a conversation."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            self.save_conversations()

    def clear_conversation(self, conversation_id: str) -> None:
        """Clear all messages from a conversation while keeping the conversation."""
        if conversation_id in self.conversations:
            self.conversations[conversation_id].messages = []
            self.conversations[conversation_id].updated_at = datetime.now()
            self.save_conversations()

    def clear_old_conversations(self) -> None:
        """Remove old conversations if over the limit."""
        if len(self.conversations) <= self.max_conversations:
            return

        # Sort by update time and keep only the most recent
        conversations = list(self.conversations.values())
        conversations.sort(key=lambda c: c.updated_at, reverse=True)

        to_keep = conversations[: self.max_conversations]
        self.conversations = {c.id: c for c in to_keep}
        self.save_conversations()

    def save_conversations(self) -> None:
        """Save conversations to storage."""
        if self.storage_type == "file":
            self._save_to_file()
        # Could add database storage here

    def load_conversations(self) -> None:
        """Load conversations from storage."""
        if self.storage_type == "file":
            self._load_from_file()
        # Could add database loading here

    def _save_to_file(self) -> None:
        """Save conversations to JSON file."""
        try:
            data = {}
            for conv_id, conversation in self.conversations.items():
                # Convert datetime objects to ISO strings for JSON serialization
                conv_dict = asdict(conversation)
                conv_dict["created_at"] = conversation.created_at.isoformat()
                conv_dict["updated_at"] = conversation.updated_at.isoformat()

                # Convert messages to dict
                conv_dict["messages"] = [asdict(msg) for msg in conversation.messages]

                data[conv_id] = conv_dict

            with open(self.file_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Error saving conversations: {e}")

    def _load_from_file(self) -> None:
        """Load conversations from JSON file."""
        if not self.file_path.exists():
            return

        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)

            for conv_id, conv_dict in data.items():
                # Convert ISO strings back to datetime objects
                conv_dict["created_at"] = datetime.fromisoformat(
                    conv_dict["created_at"]
                )
                conv_dict["updated_at"] = datetime.fromisoformat(
                    conv_dict["updated_at"]
                )

                # Convert message dicts back to Message objects
                messages = []
                for msg_dict in conv_dict.get("messages", []):
                    messages.append(Message(**msg_dict))
                conv_dict["messages"] = messages

                self.conversations[conv_id] = Conversation(**conv_dict)

        except Exception as e:
            print(f"Error loading conversations: {e}")

    def search_conversations(self, query: str) -> List[Conversation]:
        """Search conversations by title or message content."""
        results = []
        query_lower = query.lower()

        for conversation in self.conversations.values():
            # Search in title
            if query_lower in conversation.title.lower():
                results.append(conversation)
                continue

            # Search in message content
            for message in conversation.messages:
                if query_lower in message.content.lower():
                    results.append(conversation)
                    break

        # Sort by update time
        results.sort(key=lambda c: c.updated_at, reverse=True)
        return results
