"""
Pydantic models for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class NodeDefinition(BaseModel):
    """Definition of a node for graph creation."""
    id: str
    node_type: str = "standard"  # standard, branch, loop
    # For now, we don't serialize functions, so users reference by name


class EdgeDefinition(BaseModel):
    """Definition of an edge for graph creation."""
    from_node: str
    to_node: str
    conditional: bool = False  # Whether this is a conditional edge


class GraphCreateRequest(BaseModel):
    """Request to create a new graph."""
    graph_id: str
    nodes: List[NodeDefinition]
    edges: List[EdgeDefinition]
    start_node: str
    end_nodes: List[str] = []


class GraphCreateResponse(BaseModel):
    """Response from graph creation."""
    graph_id: str
    status: str = "created"


class GraphRunRequest(BaseModel):
    """Request to run a graph."""
    graph_id: str
    initial_state: Dict[str, Any] = Field(default_factory=dict)


class ExecutionLogItem(BaseModel):
    """A single execution log entry."""
    node_id: str
    status: str
    error: Optional[str] = None


class GraphRunResponse(BaseModel):
    """Response from graph execution."""
    run_id: str
    final_state: Dict[str, Any]
    execution_logs: List[ExecutionLogItem]
    status: str = "completed"


class GraphStateResponse(BaseModel):
    """Response for getting graph state."""
    run_id: str
    state: Dict[str, Any]
    logs: List[ExecutionLogItem]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    message: str
