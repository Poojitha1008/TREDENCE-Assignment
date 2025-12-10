"""
FastAPI application - Main entry point.
Exposes the workflow engine via REST API.
"""

import logging
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.engine import WorkflowGraph, GraphStore
from app.tools import ToolRegistry
from app.workflows import setup_example_workflows, setup_code_review_workflow
from app.schemas import (
    GraphCreateRequest,
    GraphCreateResponse,
    GraphRunRequest,
    GraphRunResponse,
    GraphStateResponse,
    ExecutionLogItem,
    HealthResponse,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Workflow Engine API",
    description="A minimal but complete workflow/graph engine with FastAPI",
    version="1.0.0",
)

# Initialize storage and tools
graph_store = GraphStore()
tool_registry = ToolRegistry()

# Pre-populate with example workflows
example_workflows = setup_example_workflows(tool_registry)
for workflow_name, workflow_graph in example_workflows.items():
    graph_store.save_graph(workflow_name, workflow_graph)
    logger.info(f"Registered example workflow: {workflow_name}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="Workflow engine is running",
    )


@app.post("/graph/create", response_model=GraphCreateResponse)
async def create_graph(request: GraphCreateRequest):
    """
    Create a new graph.

    For now, this is a placeholder that validates the structure.
    In production, you might:
    - Load node functions from a registry
    - Dynamically construct the graph from the definition
    - Validate the graph structure

    For demonstration, use pre-built workflows via POST /graph/run with
    graph_id like "code_review".
    """
    try:
        # Validate that nodes and edges reference each other correctly
        node_ids = {n.id for n in request.nodes}

        if request.start_node not in node_ids:
            raise ValueError(f"Start node '{request.start_node}' not in nodes")

        for end_node in request.end_nodes:
            if end_node not in node_ids:
                raise ValueError(f"End node '{end_node}' not in nodes")

        for edge in request.edges:
            if edge.from_node not in node_ids:
                raise ValueError(f"Edge references unknown node: {edge.from_node}")
            if edge.to_node not in node_ids:
                raise ValueError(f"Edge references unknown node: {edge.to_node}")

        # Store the graph ID (actual graph construction would happen here)
        graph_id = request.graph_id
        logger.info(f"Graph '{graph_id}' created with {len(request.nodes)} nodes")

        return GraphCreateResponse(graph_id=graph_id, status="created")

    except ValueError as e:
        logger.error(f"Graph creation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/graph/run", response_model=GraphRunResponse)
async def run_graph(request: GraphRunRequest):
    """
    Run a graph with initial state.

    The graph_id should reference a pre-registered graph.
    Currently supported graphs: "code_review"
    """
    try:
        # Load graph
        graph = graph_store.load_graph(request.graph_id)
        if not graph:
            raise ValueError(f"Graph '{request.graph_id}' not found")

        # Generate run ID
        run_id = str(uuid.uuid4())

        # Execute workflow
        logger.info(f"Running graph '{request.graph_id}' with run_id '{run_id}'")
        final_state, execution_logs = graph.run(request.initial_state, run_id=run_id)

        # Convert logs to response format
        log_items = [
            ExecutionLogItem(
                node_id=log.node_id,
                status=log.status,
                error=log.error,
            )
            for log in execution_logs
        ]

        # Save run for later retrieval
        graph_store.save_run(run_id, final_state, execution_logs)

        return GraphRunResponse(
            run_id=run_id,
            final_state=final_state,
            execution_logs=log_items,
            status="completed",
        )

    except ValueError as e:
        logger.error(f"Graph run error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during graph run: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/graph/state/{run_id}", response_model=GraphStateResponse)
async def get_graph_state(run_id: str):
    """
    Get the current/final state of a workflow run.
    """
    try:
        result = graph_store.load_run(run_id)
        if not result:
            raise ValueError(f"Run '{run_id}' not found")

        final_state, execution_logs = result

        log_items = [
            ExecutionLogItem(
                node_id=log.node_id,
                status=log.status,
                error=log.error,
            )
            for log in execution_logs
        ]

        return GraphStateResponse(
            run_id=run_id,
            state=final_state,
            logs=log_items,
        )

    except ValueError as e:
        logger.error(f"State retrieval error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/graphs")
async def list_graphs():
    """List all available graphs."""
    graphs = graph_store.list_graphs()
    return {
        "graphs": graphs,
        "count": len(graphs),
    }


@app.get("/runs")
async def list_runs():
    """List all completed runs."""
    runs = graph_store.list_runs()
    return {
        "runs": runs,
        "count": len(runs),
    }


@app.get("/tools")
async def list_tools():
    """List all registered tools."""
    tools = tool_registry.list_tools()
    return {
        "tools": tools,
        "count": len(tools),
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "name": "Workflow Engine API",
        "version": "1.0.0",
        "description": "A minimal but complete workflow/graph engine",
        "docs": "/docs",
        "health": "/health",
        "available_endpoints": {
            "health": "GET /health",
            "list_graphs": "GET /graphs",
            "list_runs": "GET /runs",
            "list_tools": "GET /tools",
            "create_graph": "POST /graph/create",
            "run_graph": "POST /graph/run",
            "get_state": "GET /graph/state/{run_id}",
        },
        "example_graphs": ["code_review"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
