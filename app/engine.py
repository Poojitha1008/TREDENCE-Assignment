"""
Core workflow engine - Graph execution with state management.
Supports nodes, edges, branching, and looping.
"""

from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


class NodeType(str, Enum):
    """Types of nodes in the graph."""
    STANDARD = "standard"
    BRANCH = "branch"
    LOOP = "loop"


@dataclass
class ExecutionLog:
    """Log entry for a single node execution."""
    node_id: str
    status: str  # "success", "error", "skipped"
    input_state: Dict[str, Any]
    output_state: Dict[str, Any]
    error: Optional[str] = None


@dataclass
class WorkflowNode:
    """Represents a node in the workflow graph."""
    id: str
    fn: Callable[[Dict[str, Any]], Dict[str, Any]]
    node_type: NodeType = NodeType.STANDARD
    loop_condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    max_iterations: int = 10


@dataclass
class WorkflowEdge:
    """Represents an edge in the graph."""
    from_node: str
    to_node: str
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None  # For branching


class WorkflowGraph:
    """
    A minimal workflow/graph engine.
    - Nodes: Python functions that read/modify state
    - State: Shared dictionary flowing through nodes
    - Edges: Define node connections with optional conditions
    - Branching: Conditional routing based on state
    - Looping: Repeat node execution until condition met
    """

    def __init__(self):
        self.nodes: Dict[str, WorkflowNode] = {}
        self.edges: List[WorkflowEdge] = []
        self.start_node: Optional[str] = None
        self.end_nodes: Set[str] = set()

    def add_node(
        self,
        node_id: str,
        fn: Callable[[Dict[str, Any]], Dict[str, Any]],
        node_type: NodeType = NodeType.STANDARD,
        loop_condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
        max_iterations: int = 10,
    ) -> None:
        """Add a node to the graph."""
        if node_id in self.nodes:
            raise ValueError(f"Node '{node_id}' already exists")

        self.nodes[node_id] = WorkflowNode(
            id=node_id,
            fn=fn,
            node_type=node_type,
            loop_condition=loop_condition,
            max_iterations=max_iterations,
        )

        if self.start_node is None:
            self.start_node = node_id

    def add_edge(
        self,
        from_node: str,
        to_node: str,
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> None:
        """Add an edge between nodes. Condition is for branching."""
        if from_node not in self.nodes:
            raise ValueError(f"From node '{from_node}' does not exist")
        if to_node not in self.nodes:
            raise ValueError(f"To node '{to_node}' does not exist")

        self.edges.append(
            WorkflowEdge(from_node=from_node, to_node=to_node, condition=condition)
        )

    def set_start_node(self, node_id: str) -> None:
        """Set the starting node of the workflow."""
        if node_id not in self.nodes:
            raise ValueError(f"Node '{node_id}' does not exist")
        self.start_node = node_id

    def set_end_nodes(self, node_ids: List[str]) -> None:
        """Set which nodes are terminal (end) nodes."""
        for node_id in node_ids:
            if node_id not in self.nodes:
                raise ValueError(f"Node '{node_id}' does not exist")
        self.end_nodes = set(node_ids)

    def _get_next_nodes(self, current_node: str, state: Dict[str, Any]) -> List[str]:
        """Get next nodes based on edges and branching conditions."""
        next_nodes = []
        outgoing_edges = [e for e in self.edges if e.from_node == current_node]

        for edge in outgoing_edges:
            # If there's a condition, check it
            if edge.condition is not None:
                if edge.condition(state):
                    next_nodes.append(edge.to_node)
            else:
                # No condition means always follow this edge
                next_nodes.append(edge.to_node)

        return next_nodes

    def run(
        self, initial_state: Dict[str, Any], run_id: Optional[str] = None
    ) -> tuple[Dict[str, Any], List[ExecutionLog]]:
        """
        Execute the workflow end-to-end.

        Args:
            initial_state: Starting state dictionary
            run_id: Optional ID for this run (for tracking)

        Returns:
            Tuple of (final_state, execution_logs)
        """
        if not self.start_node:
            raise ValueError("No start node defined")

        run_id = run_id or str(uuid.uuid4())
        state = initial_state.copy()
        logs: List[ExecutionLog] = []
        visited_sequence: List[str] = []

        current_node_id = self.start_node
        loop_counter: Dict[str, int] = {}  # Track loop iterations per node

        while current_node_id:
            node = self.nodes[current_node_id]
            visited_sequence.append(current_node_id)

            try:
                input_state = state.copy()

                # Check if this is a loop node
                if node.node_type == NodeType.LOOP:
                    loop_counter[current_node_id] = (
                        loop_counter.get(current_node_id, 0) + 1
                    )

                    if (
                        loop_counter[current_node_id] > node.max_iterations
                        and node.loop_condition is None
                    ):
                        raise RuntimeError(
                            f"Node '{current_node_id}' exceeded max iterations "
                            f"({node.max_iterations})"
                        )

                # Execute the node function
                result = node.fn(state)
                state.update(result)

                log_entry = ExecutionLog(
                    node_id=current_node_id,
                    status="success",
                    input_state=input_state,
                    output_state=state.copy(),
                )
                logs.append(log_entry)

                # For loop nodes, check if we should continue looping
                if node.node_type == NodeType.LOOP and node.loop_condition:
                    if node.loop_condition(state):
                        # Continue looping - stay at current node
                        logger.debug(f"Loop continues at node '{current_node_id}'")
                        continue
                    else:
                        # Condition met, exit loop
                        logger.debug(f"Loop exits node '{current_node_id}'")
                        loop_counter[current_node_id] = 0

                # Get next nodes
                next_nodes = self._get_next_nodes(current_node_id, state)

                if not next_nodes:
                    # No more nodes - we're done
                    if current_node_id not in self.end_nodes and self.end_nodes:
                        logger.warning(
                            f"Workflow ended at node '{current_node_id}' "
                            "which is not an end node"
                        )
                    current_node_id = None
                elif len(next_nodes) == 1:
                    # Single path
                    current_node_id = next_nodes[0]
                else:
                    # Multiple paths - for simplicity, take the first
                    # (In a real system, you'd handle this differently)
                    logger.warning(
                        f"Multiple next nodes from '{current_node_id}': "
                        f"{next_nodes}. Taking first."
                    )
                    current_node_id = next_nodes[0]

            except Exception as e:
                error_msg = str(e)
                log_entry = ExecutionLog(
                    node_id=current_node_id,
                    status="error",
                    input_state=input_state,
                    output_state=state.copy(),
                    error=error_msg,
                )
                logs.append(log_entry)
                logger.error(f"Error executing node '{current_node_id}': {error_msg}")
                raise

        logger.info(f"Workflow completed. Visited {len(visited_sequence)} nodes")
        return state, logs


class GraphStore:
    """In-memory store for graphs and runs."""

    def __init__(self):
        self.graphs: Dict[str, WorkflowGraph] = {}
        self.runs: Dict[str, tuple[Dict[str, Any], List[ExecutionLog]]] = {}

    def save_graph(self, graph_id: str, graph: WorkflowGraph) -> None:
        """Save a graph."""
        self.graphs[graph_id] = graph

    def load_graph(self, graph_id: str) -> Optional[WorkflowGraph]:
        """Load a graph by ID."""
        return self.graphs.get(graph_id)

    def save_run(
        self, run_id: str, state: Dict[str, Any], logs: List[ExecutionLog]
    ) -> None:
        """Save run results."""
        self.runs[run_id] = (state, logs)

    def load_run(self, run_id: str) -> Optional[tuple[Dict[str, Any], List[ExecutionLog]]]:
        """Load run results."""
        return self.runs.get(run_id)

    def list_graphs(self) -> List[str]:
        """List all graph IDs."""
        return list(self.graphs.keys())

    def list_runs(self) -> List[str]:
        """List all run IDs."""
        return list(self.runs.keys())
