import json
import os
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, name, framework_path=None):
        self.name = name
        self.framework_path = framework_path
        self.framework = self._load_framework(framework_path) if framework_path else {}
        print(f"[{self.name}] Initialized.")

    def _load_framework(self, path):
        if not os.path.exists(path):
            print(f"[{self.name}] Warning: Framework file not found at {path}")
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                # Basic MD loading logic for now, can be expanded to parse into JSON
                return {"path": path, "content": f.read()}
        except Exception as e:
            print(f"[{self.name}] Error loading framework: {e}")
            return {}

    @abstractmethod
    def handle_event(self, event_name, data):
        """Handle incoming events from the bus."""
        pass

    def emit_event(self, event_name, data):
        """Emit results back to the system's event bus."""
        message = {
            "source": self.name,
            "event": event_name,
            "payload": data
        }
        print(f"[{self.name}] >>> EMITTING: {event_name}")
        # In a real system, this would call a bridge to the main JS EventBus
        # or send a message to a Message Queue (Redis/RabbitMQ).
        return message

    def log(self, message):
        print(f"[{self.name}] {message}")
