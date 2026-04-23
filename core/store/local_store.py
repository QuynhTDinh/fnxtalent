"""
LocalStore — File-based state store for Phase 1 (Testing).
Stores all data as JSON files in a local directory.

Same interface as future SupabaseStore, so swapping is zero-effort.
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Optional

from .base_store import StateStore


class LocalStore(StateStore):
    def __init__(self, data_dir: str = "data/store"):
        self.data_dir = data_dir
        self._dirs = {
            "runs": os.path.join(data_dir, "runs"),
            "nodes": os.path.join(data_dir, "node_results"),
            "candidates": os.path.join(data_dir, "candidates"),
            "jobs": os.path.join(data_dir, "jobs"),
            "campaigns": os.path.join(data_dir, "campaigns"),
            "sessions": os.path.join(data_dir, "sessions"),
        }
        for d in self._dirs.values():
            os.makedirs(d, exist_ok=True)
        print(f"[LocalStore] Initialized at {os.path.abspath(data_dir)}")

    def _now(self):
        return datetime.now(timezone.utc).isoformat()

    def _read(self, filepath):
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _write(self, filepath, data):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    # ── Pipeline Runs ──

    def create_run(self, run_id: str, candidate_id: str, job_id: str) -> dict:
        run = {
            "id": run_id,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "status": "CREATED",
            "current_node": None,
            "created_at": self._now(),
            "updated_at": self._now(),
            "error_log": [],
        }
        self._write(os.path.join(self._dirs["runs"], f"{run_id}.json"), run)
        return run

    def update_run(self, run_id: str, **kwargs) -> dict:
        filepath = os.path.join(self._dirs["runs"], f"{run_id}.json")
        run = self._read(filepath)
        if not run:
            raise ValueError(f"Run {run_id} not found")
        run.update(kwargs)
        run["updated_at"] = self._now()
        self._write(filepath, run)
        return run

    def get_run(self, run_id: str) -> Optional[dict]:
        return self._read(os.path.join(self._dirs["runs"], f"{run_id}.json"))

    # ── Node Results ──

    def save_node_result(self, run_id: str, node_name: str,
                         status: str, output: Any,
                         duration_ms: int = 0, retries: int = 0) -> dict:
        result = {
            "run_id": run_id,
            "node_name": node_name,
            "status": status,
            "output": output,
            "duration_ms": duration_ms,
            "retries": retries,
            "created_at": self._now(),
        }
        # Use run_id subfolder for organization
        run_dir = os.path.join(self._dirs["nodes"], run_id)
        os.makedirs(run_dir, exist_ok=True)
        self._write(os.path.join(run_dir, f"{node_name}.json"), result)
        return result

    def get_node_result(self, run_id: str, node_name: str) -> Optional[dict]:
        return self._read(
            os.path.join(self._dirs["nodes"], run_id, f"{node_name}.json")
        )

    def get_all_node_results(self, run_id: str) -> list:
        run_dir = os.path.join(self._dirs["nodes"], run_id)
        if not os.path.exists(run_dir):
            return []
        results = []
        for fname in sorted(os.listdir(run_dir)):
            if fname.endswith(".json"):
                data = self._read(os.path.join(run_dir, fname))
                if data:
                    results.append(data)
        return results

    # ── Candidates ──

    def save_candidate(self, candidate: dict) -> dict:
        cid = candidate.get("id", "unknown")
        candidate["updated_at"] = self._now()
        self._write(os.path.join(self._dirs["candidates"], f"{cid}.json"), candidate)
        return candidate

    def get_candidate(self, candidate_id: str) -> Optional[dict]:
        return self._read(
            os.path.join(self._dirs["candidates"], f"{candidate_id}.json")
        )

    # ── Jobs ──

    def save_job(self, job: dict) -> dict:
        jid = job.get("id", "unknown")
        job["updated_at"] = self._now()
        self._write(os.path.join(self._dirs["jobs"], f"{jid}.json"), job)
        return job

    def get_job(self, job_id: str) -> Optional[dict]:
        return self._read(
            os.path.join(self._dirs["jobs"], f"{job_id}.json")
        )

    # ── Campaigns (Internal Audit) ──
    def save_campaign(self, campaign_id: str, data: dict) -> dict:
        data["id"] = campaign_id
        data["created_at"] = self._now()
        data["updated_at"] = self._now()
        self._write(os.path.join(self._dirs["campaigns"], f"{campaign_id}.json"), data)
        return data

    def get_campaign(self, campaign_id: str) -> Optional[dict]:
        return self._read(os.path.join(self._dirs["campaigns"], f"{campaign_id}.json"))

    def get_all_campaigns(self) -> list:
        results = []
        d = self._dirs["campaigns"]
        if not os.path.exists(d): return results
        for fname in os.listdir(d):
            if fname.endswith(".json"):
                results.append(self._read(os.path.join(d, fname)))
        return results

    # ── Sessions (Internal Audit) ──
    def save_session(self, session_id: str, data: dict) -> dict:
        data["id"] = session_id
        data["created_at"] = self._now()
        data["updated_at"] = self._now()
        self._write(os.path.join(self._dirs["sessions"], f"{session_id}.json"), data)
        return data

    def get_session(self, session_id: str) -> Optional[dict]:
        return self._read(os.path.join(self._dirs["sessions"], f"{session_id}.json"))

    def update_session(self, session_id: str, update_data: dict) -> dict:
        filepath = os.path.join(self._dirs["sessions"], f"{session_id}.json")
        session = self._read(filepath)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        session.update(update_data)
        session["updated_at"] = self._now()
        self._write(filepath, session)
        return session

    def get_sessions_by_campaign(self, campaign_id: str) -> list:
        results = []
        d = self._dirs["sessions"]
        if not os.path.exists(d): return results
        for fname in os.listdir(d):
            if fname.endswith(".json"):
                sess = self._read(os.path.join(d, fname))
                if sess and sess.get("campaign_id") == campaign_id:
                    results.append(sess)
        # sort by created_at descending
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return results
