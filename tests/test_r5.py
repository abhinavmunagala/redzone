import hashlib
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.r5_recon.agent import run_r5
from agents.r5_recon.schema import R5Input


def make_hash(scope):
    return hashlib.sha256(
        ",".join(sorted(scope)).encode()
    ).hexdigest()


# TEST 1 — happy path
def test_r5_runs():
    scope = ["linear.app"] 
    inp = R5Input(
        run_id="test-001",
        scope=scope,
        scope_hash=make_hash(scope),
        classification="C1",
        allowed_techniques=["passive_dns"],
        budget_tokens=50000
    )
    out = run_r5(inp)
    print(out.model_dump_json(indent=2))
    assert out.stop_reason is None
    assert out.run_id == "test-001"
    assert isinstance(out.subdomains, list)
    assert isinstance(out.api_surfaces, list)
    print("TEST 1 PASSED")


# TEST 2 — scope violation must fire
def test_scope_violation():
    scope = ["google.com"]
    inp = R5Input(
        run_id="test-002",
        scope=scope,
        scope_hash=make_hash(scope),
        classification="C1",
        allowed_techniques=["passive_dns"],
        budget_tokens=50000
    )
    inp.scope = ["evil.com"]  # tamper after hash
    out = run_r5(inp)
    assert out.stop_reason is not None
    assert "STOP RUN" in out.stop_reason
    print("TEST 2 PASSED — scope violation caught:", out.stop_reason)


if __name__ == "__main__":
    print("=== TEST 1: happy path ===")
    test_r5_runs()
    print("\n=== TEST 2: scope violation ===")
    test_scope_violation()
    print("\nAll tests passed.")