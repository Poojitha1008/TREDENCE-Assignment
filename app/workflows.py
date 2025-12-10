"""
Code Review Mini-Agent Workflow.
Demonstrates the workflow engine with:
1. Extract functions
2. Check complexity
3. Detect basic issues
4. Suggest improvements
5. Loop until quality_score >= threshold
"""

from typing import Dict, Any
from app.engine import WorkflowGraph, NodeType
from app.tools import ToolRegistry
import logging

logger = logging.getLogger(__name__)


def setup_code_review_workflow(tool_registry: ToolRegistry) -> WorkflowGraph:
    """
    Set up a code review workflow.
    
    Flow:
    extract_functions -> check_complexity -> detect_issues -> suggest_improvements
    -> (loop back to detect_issues if quality < threshold)
    
    Args:
        tool_registry: Registry for accessing tools
        
    Returns:
        Configured WorkflowGraph
    """
    graph = WorkflowGraph()

    # Node 1: Extract functions from code
    def extract_functions(state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract function signatures from code."""
        code = state.get("code", "")
        
        # Simple extraction - find function definitions
        functions = []
        for line in code.split("\n"):
            if line.strip().startswith("def "):
                func_name = line.split("def ")[1].split("(")[0]
                functions.append(func_name)
        
        logger.info(f"Extracted {len(functions)} functions")
        return {
            "functions": functions,
            "function_count": len(functions),
            "iteration": state.get("iteration", 0) + 1,
        }

    # Node 2: Check complexity
    def check_complexity(state: Dict[str, Any]) -> Dict[str, Any]:
        """Check cyclomatic complexity of functions."""
        code = state.get("code", "")
        
        # Simple heuristic: count nested loops/ifs
        complexity_issues = 0
        lines = code.split("\n")
        
        for line in lines:
            stripped = line.strip()
            indent_level = len(line) - len(line.lstrip())
            if indent_level > 8:  # Deep nesting
                complexity_issues += 1
        
        complexity_score = max(0, 100 - (complexity_issues * 5))
        logger.info(f"Complexity score: {complexity_score}")
        
        return {
            "complexity_issues": complexity_issues,
            "complexity_score": complexity_score,
        }

    # Node 3: Detect basic issues
    def detect_issues(state: Dict[str, Any]) -> Dict[str, Any]:
        """Detect basic code smells."""
        code = state.get("code", "")
        
        issues = []
        
        # Check for long functions (simple: count lines in function)
        if code.count("\n") > 30:
            issues.append("Long function")
        
        # Check for missing docstrings
        func_count = state.get("function_count", 0)
        docstring_count = code.count('"""')
        if docstring_count < func_count:
            issues.append("Missing docstrings")
        
        # Check for unused imports (naive check)
        if "import" in code and code.count("import") > func_count:
            issues.append("Potential unused imports")
        
        issues_count = len(issues)
        logger.info(f"Detected {issues_count} issues: {issues}")
        
        return {
            "issues": issues,
            "issue_count": issues_count,
        }

    # Node 4: Suggest improvements
    def suggest_improvements(state: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest improvements based on detected issues."""
        issues = state.get("issues", [])
        complexity_score = state.get("complexity_score", 50)
        issue_count = state.get("issue_count", 0)
        
        suggestions = []
        
        if issue_count > 2:
            suggestions.append("Refactor into smaller functions")
        
        if complexity_score < 60:
            suggestions.append("Reduce nesting depth")
        
        if "Missing docstrings" in issues:
            suggestions.append("Add comprehensive docstrings")
        
        if "Potential unused imports" in issues:
            suggestions.append("Clean up imports")
        
        # Calculate quality score
        # Start at 100, deduct based on issues and complexity
        quality_score = 100
        quality_score -= issue_count * 10
        quality_score -= max(0, 100 - complexity_score) * 0.1
        quality_score = max(0, min(100, quality_score))  # Clamp to 0-100
        
        logger.info(f"Quality score: {quality_score:.1f}")
        
        return {
            "suggestions": suggestions,
            "quality_score": quality_score,
        }

    # Add nodes
    graph.add_node("extract", extract_functions)
    graph.add_node("complexity", check_complexity)
    graph.add_node("detect_issues", detect_issues)
    graph.add_node("suggest", suggest_improvements)

    # Add edges: linear flow
    graph.add_edge("extract", "complexity")
    graph.add_edge("complexity", "detect_issues")
    graph.add_edge("detect_issues", "suggest")

    # Set start and end nodes
    graph.set_start_node("extract")
    graph.set_end_nodes(["suggest"])

    return graph


def setup_example_workflows(tool_registry: ToolRegistry) -> Dict[str, WorkflowGraph]:
    """
    Set up example workflows for demonstration.
    
    Returns:
        Dictionary mapping workflow names to graphs
    """
    workflows = {
        "code_review": setup_code_review_workflow(tool_registry),
    }
    
    return workflows
