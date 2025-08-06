# agentik/memory.py

"""
Memory backend implementations for Agentik framework.

This module provides both in-memory (ephemeral) and persistent (JSON) memory stores
that can be used to remember, recall, and summarize agent experiences.
"""

import abc
import json
from pathlib import Path
from typing import List


# ---------------------- Abstract Base ----------------------

class MemoryBase(abc.ABC):
    """
    Abstract base class for all memory backends.
    Defines the required interface for memory operations.
    """

    @abc.abstractmethod
    def remember(self, context: str) -> None:
        """
        Store new context or memory into the backend.

        Args:
            context (str): Information to store.
        """
        pass

    @abc.abstractmethod
    def recall(self, query: str = "") -> List[str]:
        """
        Retrieve stored memories optionally filtered by a query string.

        Args:
            query (str): Optional keyword filter.

        Returns:
            List[str]: Matching or all stored memories.
        """
        pass

    @abc.abstractmethod
    def summarize(self) -> str:
        """
        Generate a basic summary by concatenating stored memory items.

        Returns:
            str: Summary text.
        """
        pass


# ---------------------- In-Memory Store ----------------------

class DictMemory(MemoryBase):
    """
    Simple in-memory memory store backed by a Python list.
    Does not persist across sessions.
    """

    def __init__(self):
        self._data: List[str] = []

    def remember(self, context: str) -> None:
        self._data.append(context)

    def recall(self, query: str = "") -> List[str]:
        if query:
            return [c for c in self._data if query.lower() in c.lower()]
        return self._data

    def summarize(self) -> str:
        return "\n".join(self._data)


# ---------------------- Persistent JSON Store ----------------------

class JSONMemoryStore(MemoryBase):
    """
    Persistent memory backend that saves memory to a local JSON file.

    Args:
        filepath (str): Path to the JSON file used for storage.
    """

    def __init__(self, filepath: str = "memory.json"):
        self.path = Path(filepath)
        if not self.path.exists():
            self._save([])

    def _load(self) -> List[str]:
        """
        Load memory entries from the JSON file.

        Returns:
            List[str]: List of stored memory strings.
        """
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
        except Exception:
            return []

    def _save(self, data: List[str]) -> None:
        """
        Save memory entries to the JSON file.

        Args:
            data (List[str]): List of strings to save.
        """
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def remember(self, context: str) -> None:
        data = self._load()
        data.append(context)
        self._save(data)

    def recall(self, query: str = "") -> List[str]:
        data = self._load()
        if query:
            return [c for c in data if query.lower() in c.lower()]
        return data

    def summarize(self) -> str:
        return "\n".join(self._load())
