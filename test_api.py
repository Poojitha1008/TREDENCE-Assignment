"""
Test script to call the FastAPI endpoints.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint."""
    print("\n" + "=" * 80)
    print("Testing Health Check")
    print("=" * 80)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_list_graphs():
    """Test list graphs endpoint."""
    print("\n" + "=" * 80)
    print("Testing List Graphs")
    print("=" * 80)
    
    response = requests.get(f"{BASE_URL}/graphs")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_run_workflow():
    """Test running a workflow."""
    print("\n" + "=" * 80)
    print("Testing Run Workflow")
    print("=" * 80)
    
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
    
    payload = {
        "graph_id": "code_review",
        "initial_state": {
            "code": sample_code
        }
    }
    
    response = requests.post(f"{BASE_URL}/graph/run", json=payload)
    print(f"Status Code: {response.status_code}")
    result = response.json()
    
    print(f"\nRun ID: {result.get('run_id')}")
    print(f"Status: {result.get('status')}")
    
    final_state = result.get('final_state', {})
    print(f"\nFinal State:")
    print(f"  - Functions: {final_state.get('functions')}")
    print(f"  - Quality Score: {final_state.get('quality_score')}")
    print(f"  - Issues: {final_state.get('issues')}")
    print(f"  - Suggestions: {final_state.get('suggestions')}")
    
    print(f"\nExecution Logs ({len(result.get('logs', []))} entries):")
    for i, log in enumerate(result.get('logs', []), 1):
        print(f"  {i}. {log['node_id']}: {log['status']}")
    
    return result.get('run_id')


def test_get_run_state(run_id):
    """Test getting run state."""
    print("\n" + "=" * 80)
    print(f"Testing Get Run State for {run_id}")
    print("=" * 80)
    
    response = requests.get(f"{BASE_URL}/graph/state/{run_id}")
    print(f"Status Code: {response.status_code}")
    result = response.json()
    
    print(f"Status: {result.get('status')}")
    print(f"Final State Keys: {list(result.get('final_state', {}).keys())}")
    print(f"Log Entries: {len(result.get('logs', []))}")


if __name__ == "__main__":
    # Wait for server to be ready
    time.sleep(2)
    
    try:
        test_health()
        test_list_graphs()
        run_id = test_run_workflow()
        test_get_run_state(run_id)
        
        print("\n" + "=" * 80)
        print("✓ All API tests passed!")
        print("=" * 80)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise
