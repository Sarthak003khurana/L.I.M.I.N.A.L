"""
Integration tests for L.I.M.I.N.A.L. FastAPI Backend Endpoints
Verifies /health, /analyze (with parallel executor & caching), and /analyze/stream (SSE).
"""
import sys
import time
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    print("[TEST] Checking /health...")
    resp = requests.get(f"{BASE_URL}/health", timeout=5)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data.get("status") == "healthy"
    assert data.get("models_loaded") is True
    print(f"  [PASS] /health OK - Device: {data.get('device')}, Azure: {data.get('azure_explainer')}")

def test_analyze_local_fast():
    print("[TEST] Checking POST /analyze (include_azure=False)...")
    sample_text = "I'm fine with whatever you decide. The current plan should probably work."
    t0 = time.time()
    resp = requests.post(
        f"{BASE_URL}/analyze",
        json={"text": sample_text, "include_azure": False},
        timeout=10,
    )
    t1 = time.time()
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "dossier" in data, "Missing dossier in response"
    assert "agents" in data, "Missing agents in response"
    for agent in ["archaeologist", "psychologist", "logician", "historian", "synthesizer"]:
        assert agent in data["agents"], f"Missing agent {agent}"
    duration = t1 - t0
    print(f"  [PASS] /analyze OK in {duration:.3f}s. Prediction: {data['dossier'].get('primary_pattern')}")

def test_cache_hit():
    print("[TEST] Checking in-memory LRU cache speed...")
    sample_text = "I'm fine with whatever you decide. The current plan should probably work."
    t0 = time.time()
    resp = requests.post(
        f"{BASE_URL}/analyze",
        json={"text": sample_text, "include_azure": False},
        timeout=5,
    )
    t1 = time.time()
    assert resp.status_code == 200
    cache_duration = t1 - t0
    print(f"  [PASS] Cache hit response time: {cache_duration:.4f}s")
    assert cache_duration < 0.1, f"Expected cache hit < 0.1s, got {cache_duration}s"

def test_analyze_stream():
    print("[TEST] Checking POST /analyze/stream (SSE)...")
    sample_text = "Let us table this discussion until the quarterly numbers are audited."
    resp = requests.post(
        f"{BASE_URL}/analyze/stream",
        json={"text": sample_text, "include_azure": False},
        stream=True,
        timeout=10,
    )
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers.get("content-type", "")

    events_received = []
    for line in resp.iter_lines(decode_unicode=True):
        if line and line.startswith("data: "):
            events_received.append(line[6:])

    assert len(events_received) >= 4, f"Expected at least 4 SSE events, got {len(events_received)}"
    print(f"  [PASS] /analyze/stream received {len(events_received)} SSE events successfully")

def test_remediate():
    print("[TEST] Checking POST /remediate...")
    resp = requests.post(
        f"{BASE_URL}/remediate",
        json={
            "text": "I am fine with whatever you decide. The current plan should probably work.",
            "dossier": {
                "primary_pattern": "UNSTATED_PREFERENCE",
                "strategically_missing": ["Explicit preference", "Definite timeline"]
            }
        },
        timeout=10,
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert "direct" in data, "Missing direct rewrite"
    assert "diplomatic" in data, "Missing diplomatic rewrite"
    assert len(data["direct"]) > 5
    print(f"  [PASS] /remediate OK. Engine: {data.get('engine')}")

def test_extract_pdf():
    print("[TEST] Checking POST /extract-pdf...")
    with open("sample_executive_memo.pdf", "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/extract-pdf",
            files={"file": ("sample_executive_memo.pdf", f, "application/pdf")},
            timeout=10,
        )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data.get("pages") == 1
    assert "We are fine with whatever" in data.get("text", "")
    print(f"  [PASS] /extract-pdf OK. Extracted {data.get('characters')} chars from {data.get('filename')}")

if __name__ == "__main__":
    try:
        test_health()
        test_analyze_local_fast()
        test_cache_hit()
        test_analyze_stream()
        test_remediate()
        test_extract_pdf()
        print("\n>>> ALL API INTEGRATION TESTS (6/6) PASSED! <<<")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        sys.exit(1)
