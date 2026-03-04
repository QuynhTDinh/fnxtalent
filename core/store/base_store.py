"""
StateStore — Abstract interface for pipeline state persistence.

Phase 1: LocalStore (JSON files)
Phase 2: SupabaseStore (drop-in replacement)

All stores implement the same interface so the DAG engine
never needs to know which backend is being used.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import datetime


class StateStore(ABC):
    """Abstract base for state storage backends."""

    # ── Pipeline Runs ──

    @abstractmethod
    def create_run(self, run_id: str, candidate_id: str, job_id: str) -> dict:
        """Create a new pipeline run record."""
        pass

    @abstractmethod
    def update_run(self, run_id: str, **kwargs) -> dict:
        """Update a pipeline run (status, current_node, etc.)."""
        pass

    @abstractmethod
    def get_run(self, run_id: str) -> Optional[dict]:
        """Get a pipeline run by ID."""
        pass

    # ── Node Results ──

    @abstractmethod
    def save_node_result(self, run_id: str, node_name: str,
                         status: str, output: Any,
                         duration_ms: int = 0, retries: int = 0) -> dict:
        """Save the result of a node execution."""
        pass

    @abstractmethod
    def get_node_result(self, run_id: str, node_name: str) -> Optional[dict]:
        """Get the result of a specific node in a run."""
        pass

    @abstractmethod
    def get_all_node_results(self, run_id: str) -> list:
        """Get all node results for a pipeline run."""
        pass

    # ── Candidates ──

    @abstractmethod
    def save_candidate(self, candidate: dict) -> dict:
        """Save or update a candidate profile."""
        pass

    @abstractmethod
    def get_candidate(self, candidate_id: str) -> Optional[dict]:
        """Get a candidate by ID."""
        pass

    # ── Jobs ──

    @abstractmethod
    def save_job(self, job: dict) -> dict:
        """Save or update a job/JD."""
        pass

    @abstractmethod
    def get_job(self, job_id: str) -> Optional[dict]:
        """Get a job by ID."""
        pass
