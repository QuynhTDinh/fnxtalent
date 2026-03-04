"""
BaseAgent - Standardized base class for all FNX Python agents.
"""

import os
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    def __init__(self, name, framework_path=None):
        self.name = name
        self.framework_path = framework_path
        self.framework = self._load_framework(framework_path) if framework_path else {}

    def _load_framework(self, path):
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return {"path": path, "content": f.read()}
        except Exception as e:
            self.log(f"Error loading framework: {e}")
            return {}

    @abstractmethod
    def handle_event(self, event_name, data):
        """Handle incoming events."""
        pass

    def emit_event(self, event_name, data):
        """Emit results (logged only — routing handled by DAG engine)."""
        message = {
            "source": self.name,
            "event": event_name,
            "payload": data
        }
        self.log(f">>> EMITTING: {event_name}")
        return message

    def log(self, message):
        print(f"[{self.name}] {message}")
