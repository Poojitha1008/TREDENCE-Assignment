"""
Local API test using FastAPI TestClient (no network, no uvicorn needed).
"""
from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    print("/health ->", resp.status_code, resp.json())


def test_list_graphs():
    resp = client.get("/graphs")
    print("/graphs ->", resp.status_code, resp.json())


def test_run_workflow():
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
    payload = {"graph_id": "code_review", "initial_state": {"code": sample_code}}
    resp = client.post("/graph/run", json=payload)
    print("/graph/run ->", resp.status_code)
    result = resp.json()
    print(json.dumps(result.get("final_state", {}), indent=2))
    return result.get("run_id")


def test_get_run_state(run_id):
    resp = client.get(f"/graph/state/{run_id}")
    print(f"/graph/state/{run_id} ->", resp.status_code)
    print(json.dumps(resp.json(), indent=2))


if __name__ == '__main__':
    test_health()
    test_list_graphs()
    run_id = test_run_workflow()
    if run_id:
        test_get_run_state(run_id)
    print('\n✓ Local tests completed')
