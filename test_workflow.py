"""
Test script to demonstrate the workflow engine.
Run this to see the Code Review workflow in action.
"""

import json
from app.engine import WorkflowGraph
from app.tools import ToolRegistry
from app.workflows import setup_code_review_workflow


def test_code_review_workflow():
    """Test the code review workflow."""
    print("=" * 80)
    print("Testing Code Review Workflow")
    print("=" * 80)

    # Set up tools (not used in this example, but shows extensibility)
    tool_registry = ToolRegistry()

    # Create workflow
    workflow = setup_code_review_workflow(tool_registry)

    # Sample code to review
    sample_code = '''def process_data(items):
    for item in items:
        if item["type"] == "active":
            for sub_item in item["children"]:
                if sub_item["value"] > 100:
                    if sub_item["valid"]:
                        print(f"Processing {sub_item}")

def clean_input(data):
    return data.strip()
'''

    # Run workflow
    initial_state = {"code": sample_code}

    print("\nInitial State:")
    print(json.dumps(initial_state, indent=2))
    print("\n" + "-" * 80)

    try:
        final_state, logs = workflow.run(initial_state)

        print("\nExecution Logs:")
        for i, log in enumerate(logs, 1):
            print(f"\n{i}. Node: {log.node_id}")
            print(f"   Status: {log.status}")
            if log.error:
                print(f"   Error: {log.error}")

        print("\n" + "-" * 80)
        print("\nFinal State:")

        # Pretty print final state
        output_state = {
            k: v
            for k, v in final_state.items()
            if k != "code"  # Don't print the full code
        }
        print(json.dumps(output_state, indent=2))

        print("\n" + "=" * 80)
        print("✓ Workflow completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Error during workflow: {e}")
        raise


if __name__ == "__main__":
    test_code_review_workflow()
