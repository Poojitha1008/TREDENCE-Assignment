# Workflow Engine - AI Engineering Assignment

A minimal but complete workflow/graph engine built with FastAPI, similar to a simplified version of LangGraph.

## Overview

This project implements:

1. **Workflow Graph Engine** - Execute sequences of nodes with shared state
2. **Branching & Looping** - Conditional routing and iterative execution
3. **Tool Registry** - Functions that nodes can call
4. **FastAPI REST API** - Run workflows via HTTP
5. **Code Review Workflow** - Example workflow demonstrating all features

## Features Implemented

### Core Engine (`app/engine.py`)

- **Nodes**: Python functions that read and modify shared state
- **State**: Dictionary flowing through nodes
- **Edges**: Connect nodes with optional branching conditions
- **Branching**: Conditional routing based on state values
- **Looping**: Repeat node execution until condition is met
- **Execution Logging**: Track each node's input/output and status

### Workflow Graph

```python
graph = WorkflowGraph()
graph.add_node("extract", extract_functions)
graph.add_node("analyze", analyze_code)
graph.add_edge("extract", "analyze")
graph.set_start_node("extract")

state, logs = graph.run({"code": "..."})
```

### Tool Registry (`app/tools.py`)

Simple registry for tools (functions) that nodes can use:

```python
registry = ToolRegistry()
registry.register("detect_smells", detect_code_smells)
tool_result = registry.call("detect_smells", code="...")
```

### Example Workflow: Code Review Mini-Agent

Located in `app/workflows.py`. Demonstrates:

1. **Extract Functions** - Parse function signatures from code
2. **Check Complexity** - Analyze nesting depth and complexity
3. **Detect Issues** - Identify code smells (missing docstrings, long functions, etc.)
4. **Suggest Improvements** - Generate suggestions based on issues
5. **Looping** - Re-run detection if quality score < 70 (up to 3 iterations)

## API Endpoints

### Health & Info

```bash
GET /health              # Health check
GET /                    # API info
GET /graphs              # List available graphs
GET /runs                # List all completed runs
GET /tools               # List registered tools
```

### Graph Operations

```bash
POST /graph/create       # Create a new graph (validation only)
POST /graph/run          # Execute a graph
GET /graph/state/{run_id}  # Get run state and logs
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python -m uvicorn app.main:app --reload
```

Server runs on `http://localhost:8000`

### 3. Try the API

**Health check:**
```bash
curl http://localhost:8000/health
```

**Run code review workflow:**
```bash
curl -X POST http://localhost:8000/graph/run \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "code_review",
    "initial_state": {
      "code": "def extract_name(data):\n  for item in data:\n    if item[\"type\"] == \"name\":\n      return item[\"value\"]\n  return None"
    }
  }'
```

**Get execution results:**
```bash
curl http://localhost:8000/graph/state/{run_id}
```

### 4. Interactive API Docs

Visit `http://localhost:8000/docs` for interactive Swagger UI.

## Project Structure

```
app/
├── __init__.py           # Package init
├── main.py               # FastAPI application
├── engine.py             # Core graph engine (WorkflowGraph, GraphStore)
├── tools.py              # Tool registry
├── workflows.py          # Example workflows (code_review)
├── schemas.py            # Pydantic models for API validation
requirements.txt          # Python dependencies
README.md                 # This file
```

## Design Decisions

1. **In-Memory Storage**: Used in-memory dictionaries for simplicity. For production, replace with SQLite/PostgreSQL.

2. **Simple Node Execution**: Nodes are pure functions. State is passed as dict, modified in-place.

3. **Branching**: Handled via optional conditions on edges. If condition returns True, that edge is taken.

4. **Looping**: Marked nodes as `LOOP` type with a condition that determines when to exit.

5. **Error Handling**: Errors are logged and included in execution logs. Workflow stops on error.

6. **Logging**: Uses Python's standard logging module for visibility into execution flow.

## What Would Be Improved With More Time

1. **Persistent Storage**: SQLite or PostgreSQL instead of in-memory storage
2. **WebSocket Support**: Stream execution logs in real-time to clients
3. **Async Execution**: Use `asyncio` and `async def` for long-running tasks
4. **Graph Visualization**: Endpoint returning graph structure for visualization
5. **Dynamic Node Registration**: Allow registering node functions via API
6. **Error Recovery**: Implement retry logic for failed nodes
7. **Conditional Branching**: Support multiple output paths from a single node
8. **Nested Graphs**: Allow graphs to call other graphs
9. **Authentication**: Add API authentication/authorization
10. **Metrics**: Prometheus metrics for monitoring execution times, errors, etc.
11. **Graph Versioning**: Track changes to graph definitions
12. **Testing**: Comprehensive unit and integration tests

## Example Response

### Running Code Review Workflow

```json
{
  "run_id": "abc123",
  "final_state": {
    "code": "def extract_name(data):\n  for item in data:\n    if item[\"type\"] == \"name\":\n      return item[\"value\"]\n  return None",
    "functions": ["extract_name"],
    "function_count": 1,
    "iteration": 1,
    "complexity_issues": 1,
    "complexity_score": 95,
    "issues": ["Missing docstrings"],
    "issue_count": 1,
    "suggestions": ["Add comprehensive docstrings"],
    "quality_score": 90.0
  },
  "execution_logs": [
    {
      "node_id": "extract",
      "status": "success",
      "error": null
    },
    {
      "node_id": "complexity",
      "status": "success",
      "error": null
    },
    {
      "node_id": "detect_issues",
      "status": "success",
      "error": null
    },
    {
      "node_id": "suggest",
      "status": "success",
      "error": null
    }
  ],
  "status": "completed"
}
```

## Technical Highlights

- **Clean Architecture**: Separation of concerns (engine, tools, workflows, API)
- **Type Hints**: Full type annotations for clarity
- **Pydantic Validation**: Request/response validation
- **Logging**: Comprehensive logging for debugging
- **Error Handling**: Graceful error handling with informative messages
- **Extensible Design**: Easy to add new nodes, edges, and tools

## Testing

To test the workflow manually:

1. Start the server
2. Use the Swagger UI at `/docs`
3. Or use curl commands provided above

## Notes

- The current implementation uses pre-registered workflows (e.g., "code_review")
- Node functions must be registered in `app/workflows.py`
- State is a simple dictionary that flows through the graph
- Execution is synchronous; for async/background tasks, see "Future Improvements"

Enjoy building with this minimal but powerful workflow engine!
