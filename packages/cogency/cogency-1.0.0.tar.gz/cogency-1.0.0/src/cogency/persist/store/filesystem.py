"""Filesystem persistence store - local state management with file locking."""

import json
import os
import uuid
from dataclasses import asdict
from fcntl import LOCK_EX, LOCK_UN, flock
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from cogency.persist.serialize import serialize_profile
from cogency.state import AgentState

from .base import Store


class Filesystem(Store):
    """File-based state persistence with atomic operations and process isolation."""

    def __init__(self, base_dir: str = None):
        from ...config import PathsConfig

        if base_dir is None:
            base_dir = PathsConfig().state
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Create memory subdirectory for user profiles
        self.memory_dir = self.base_dir / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self.process_id = str(uuid.uuid4())[:8]  # Unique process ID for isolation

    def _get_state_path(self, state_key: str) -> Path:
        """Get file path for state key."""
        # Handle profile keys with clean directory structure
        if state_key.startswith("profile:"):
            user_id = state_key.replace("profile:", "")
            safe_user_id = user_id.replace("/", "_").replace(":", "_")
            return self.memory_dir / f"{safe_user_id}.json"

        # Legacy format for other state keys
        safe_key = state_key.replace(":", "_").replace("/", "_")
        return self.base_dir / f"{safe_key}_{self.process_id}.json"

    async def save(self, state_key: str, state: Union[AgentState, Dict[str, Any]]) -> bool:
        """Save state atomically with file locking."""
        try:
            state_path = self._get_state_path(state_key)
            temp_path = state_path.with_suffix(".tmp")

            # Handle both AgentState objects and raw dicts (for memory system)
            if isinstance(state, dict):
                state_data = {"state": state, "process_id": self.process_id}
            else:
                # Prepare serializable state data for AgentState
                state_data = {
                    "state": {
                        "execution": asdict(state.execution),
                        "reasoning": asdict(state.reasoning),
                        "user_profile": (serialize_profile(state.user) if state.user else None),
                    },
                    "process_id": self.process_id,
                }

            # Atomic write: write to temp file first, then rename
            with open(temp_path, "w") as f:
                flock(f.fileno(), LOCK_EX)  # Exclusive lock
                json.dump(state_data, f, indent=2, default=str)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
                flock(f.fileno(), LOCK_UN)  # Release lock

            # Atomic rename
            temp_path.rename(state_path)
            return True

        except Exception:
            # Clean up temp file on error
            if temp_path.exists():
                temp_path.unlink()
            return False

    async def load(self, state_key: str) -> Optional[Dict[str, Any]]:
        """Load state with validation."""
        try:
            state_path = self._get_state_path(state_key)
            if not state_path.exists():
                return None

            with open(state_path) as f:
                flock(f.fileno(), LOCK_EX)  # Shared lock for reading
                data = json.load(f)
                flock(f.fileno(), LOCK_UN)

            return data

        except Exception:
            return None

    async def delete(self, state_key: str) -> bool:
        """Delete state file."""
        try:
            state_path = self._get_state_path(state_key)
            if state_path.exists():
                state_path.unlink()
            return True
        except Exception:
            return False

    async def list_states(self, user_id: str) -> List[str]:
        """List all state files for a user."""
        try:
            # Convert user_id to safe format for pattern matching
            safe_user_id = user_id.replace(":", "_").replace("/", "_")
            pattern = f"{safe_user_id}_*_{self.process_id}.json"
            matches = list(self.base_dir.glob(pattern))

            # Convert back from safe format to original key format
            result = []
            safe_user_id_len = len(safe_user_id)
            for match in matches:
                # Remove process ID suffix
                stem_without_process = match.stem.replace(f"_{self.process_id}", "")
                # Extract the part after the safe user_id
                session_part = stem_without_process[safe_user_id_len + 1 :]  # +1 for the _
                # Reconstruct original key format
                original_key = f"{user_id}:{session_part}"
                result.append(original_key)
            return result
        except Exception:
            return []
