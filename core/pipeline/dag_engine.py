"""
DAG Pipeline Engine — Smart orchestrator for FNX Talent Factory.

Unlike a simple sequential pipeline, this engine:
- Executes independent nodes IN PARALLEL (asyncio)
- Supports CROSS-VALIDATION nodes that check results of upstream nodes
- Retries failed nodes (configurable)
- Persists all state through the StateStore (LocalStore or SupabaseStore)
- Can RESUME a failed pipeline from the last successful node

Architecture:
    Nodes are registered with dependencies.
    The engine resolves the dependency graph and runs
    nodes whose dependencies are all satisfied.
"""

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from core.store.base_store import StateStore


class NodeStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    RETRYING = "RETRYING"


@dataclass
class NodeDef:
    """Definition of a pipeline node."""
    name: str
    handler: Callable  # async def handler(context: dict) -> Any
    depends_on: List[str] = field(default_factory=list)
    max_retries: int = 2
    is_validator: bool = False  # Cross-validation node
    on_fail: str = "stop"  # "stop" | "retry_upstream" | "skip"


class DAGEngine:
    """
    DAG-based pipeline executor with parallel execution,
    cross-validation, retry, and persistent state.
    """

    def __init__(self, store: StateStore):
        self.store = store
        self.nodes: Dict[str, NodeDef] = {}
        self._log_prefix = "[DAGEngine]"

    def add_node(self, name: str, handler: Callable,
                 depends_on: List[str] = None,
                 max_retries: int = 2,
                 is_validator: bool = False,
                 on_fail: str = "stop"):
        """Register a node in the pipeline DAG."""
        self.nodes[name] = NodeDef(
            name=name,
            handler=handler,
            depends_on=depends_on or [],
            max_retries=max_retries,
            is_validator=is_validator,
            on_fail=on_fail,
        )
        self._log(f"Registered node: {name} (depends: {depends_on or '[]'})")

    def _log(self, msg):
        print(f"{self._log_prefix} {msg}")

    async def run(self, candidate_data: dict, job_data: dict,
                  run_id: str = None) -> dict:
        """
        Execute the full pipeline.

        Returns a dict with all node results and the final pipeline status.
        """
        run_id = run_id or f"run_{uuid.uuid4().hex[:8]}"
        candidate_id = candidate_data.get("id", "unknown")
        job_id = job_data.get("id", "unknown")

        # Create pipeline run record
        self.store.create_run(run_id, candidate_id, job_id)
        self.store.save_candidate(candidate_data)
        self.store.save_job(job_data)

        self._log(f"{'='*60}")
        self._log(f"Pipeline RUN: {run_id}")
        self._log(f"Candidate: {candidate_data.get('fullName')} ({candidate_id})")
        self._log(f"Job: {job_data.get('title', job_id)}")
        self._log(f"Nodes: {list(self.nodes.keys())}")
        self._log(f"{'='*60}")

        # Build execution context (shared mutable state between nodes)
        context = {
            "run_id": run_id,
            "candidate": candidate_data,
            "job": job_data,
            "results": {},  # node_name -> output
            "statuses": {},  # node_name -> NodeStatus
        }

        # Initialize all nodes as PENDING
        for name in self.nodes:
            context["statuses"][name] = NodeStatus.PENDING

        # Execute DAG
        try:
            await self._execute_dag(context)
        except Exception as e:
            self._log(f"Pipeline FAILED: {e}")
            self.store.update_run(run_id, status="FAILED", error_log=[str(e)])

        # Determine final status
        all_statuses = context["statuses"]
        if all(s == NodeStatus.SUCCESS for s in all_statuses.values()):
            final_status = "COMPLETED"
        elif any(s == NodeStatus.FAILED for s in all_statuses.values()):
            final_status = "PARTIAL_FAILURE"
        else:
            final_status = "UNKNOWN"

        self.store.update_run(run_id, status=final_status)

        self._log(f"Pipeline {final_status}: {run_id}")
        self._log(f"Node statuses: {dict(all_statuses)}")

        return {
            "run_id": run_id,
            "status": final_status,
            "results": context["results"],
            "statuses": {k: v.value for k, v in context["statuses"].items()},
        }

    async def _execute_dag(self, context: dict):
        """
        Core DAG execution loop.
        Repeatedly finds nodes whose dependencies are met and runs them.
        Supports parallel execution of independent nodes.
        """
        max_iterations = len(self.nodes) * 3  # Safety limit
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Find nodes ready to run (all deps satisfied, status is PENDING)
            ready = []
            for name, node in self.nodes.items():
                if context["statuses"][name] != NodeStatus.PENDING:
                    continue
                deps_met = all(
                    context["statuses"].get(dep) == NodeStatus.SUCCESS
                    for dep in node.depends_on
                )
                if deps_met:
                    ready.append(node)

            if not ready:
                # Check if we're stuck (some nodes PENDING but deps not met)
                pending = [n for n, s in context["statuses"].items()
                          if s == NodeStatus.PENDING]
                if not pending:
                    break  # All done
                
                # Check for failed dependencies
                has_failed_deps = False
                for pname in pending:
                    pnode = self.nodes[pname]
                    for dep in pnode.depends_on:
                        if context["statuses"].get(dep) == NodeStatus.FAILED:
                            has_failed_deps = True
                            context["statuses"][pname] = NodeStatus.SKIPPED
                            self._log(f"SKIPPED: {pname} (dependency {dep} failed)")
                
                if not has_failed_deps:
                    break  # Shouldn't happen, but safety exit
                continue

            # Execute ready nodes in parallel
            self._log(f"Executing in parallel: {[n.name for n in ready]}")

            tasks = [self._execute_node(node, context) for node in ready]
            await asyncio.gather(*tasks)

        self._log("DAG execution complete.")

    async def _execute_node(self, node: NodeDef, context: dict):
        """Execute a single node with retry logic."""
        run_id = context["run_id"]
        retries = 0

        while retries <= node.max_retries:
            context["statuses"][node.name] = NodeStatus.RUNNING
            self.store.update_run(run_id, current_node=node.name)

            self._log(f"▶ {node.name} {'(retry #'+str(retries)+')' if retries > 0 else ''}")
            start_time = time.time()

            try:
                # Run the handler (may be sync or async)
                if asyncio.iscoroutinefunction(node.handler):
                    result = await node.handler(context)
                else:
                    result = node.handler(context)

                duration_ms = int((time.time() - start_time) * 1000)

                # For validator nodes, check if result indicates pass/fail
                if node.is_validator and isinstance(result, dict):
                    if not result.get("valid", True):
                        raise ValidationError(
                            f"Validation failed: {result.get('reason', 'unknown')}"
                        )

                # Success!
                context["results"][node.name] = result
                context["statuses"][node.name] = NodeStatus.SUCCESS

                self.store.save_node_result(
                    run_id, node.name, "SUCCESS", result,
                    duration_ms=duration_ms, retries=retries,
                )

                self._log(f"✓ {node.name} completed ({duration_ms}ms)")
                return

            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                self._log(f"✗ {node.name} failed: {e}")

                retries += 1
                if retries <= node.max_retries:
                    context["statuses"][node.name] = NodeStatus.RETRYING
                    self._log(f"  Retrying {node.name} ({retries}/{node.max_retries})...")
                    await asyncio.sleep(1)  # Brief pause before retry
                else:
                    context["statuses"][node.name] = NodeStatus.FAILED
                    self.store.save_node_result(
                        run_id, node.name, "FAILED", {"error": str(e)},
                        duration_ms=duration_ms, retries=retries - 1,
                    )
                    self.store.update_run(
                        run_id,
                        error_log=[f"{node.name}: {e}"],
                    )

                    if node.on_fail == "skip":
                        context["statuses"][node.name] = NodeStatus.SKIPPED
                        self._log(f"  {node.name} skipped (on_fail=skip)")
                    return


class ValidationError(Exception):
    """Raised when a cross-validation node rejects the results."""
    pass
