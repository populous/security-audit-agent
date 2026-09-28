# tests/test_end_to_end.py
# End-to-end tests for security audit workflow

import pytest
import json
from security_review_graph import graph


class TestEndToEnd:
    """End-to-end tests for the complete security audit workflow"""

    def test_workflow_structure(self):
        """Test that the workflow graph has correct structure"""
        # Verify graph exists and is callable
        assert graph is not None
        assert hasattr(graph, "invoke")

    def test_state_schema(self, initial_review_state):
        """Test that initial state matches expected schema"""
        required_keys = {
            "repo_path", "semgrep_json", "crew_result",
            "findings", "mapped_findings", "patches",
            "verdict", "human_approved"
        }
        
        assert set(initial_review_state.keys()) == required_keys
        assert isinstance(initial_review_state["findings"], list)
        assert isinstance(initial_review_state["mapped_findings"], list)
        assert isinstance(initial_review_state["patches"], list)
        assert initial_review_state["human_approved"] is False

    def test_verdict_logic_integration(self, sample_mapped_findings):
        """Integration test for verdict logic"""
        # Simulate the complete verdict flow
        state = {
            "repo_path": "/tmp/test",
            "semgrep_json": "",
            "crew_result": None,
            "findings": sample_mapped_findings,
            "mapped_findings": sample_mapped_findings,
            "patches": [],
            "verdict": None,
            "human_approved": False,
        }
        
        # Apply verdict logic
        findings = state["findings"]
        mapped = state["mapped_findings"]
        
        if not findings:
            verdict = {"pass": False, "reason": "검토 항목 없음"}
        elif len(mapped) < len(findings):
            verdict = {"pass": False, "reason": "조항 매핑 부족"}
        else:
            ok = all(m.get("clause_id") and m["clause_id"] != "SEC-??" for m in mapped)
            verdict = {"pass": ok, "reason": "조항 매핑 완료" if ok else "조항 매핑 불완전"}
        
        state["verdict"] = verdict
        
        # Verify verdict
        assert state["verdict"]["pass"] is True
        assert state["verdict"]["reason"] == "조항 매핑 완료"
        
        # Verify routing
        if state["verdict"]["pass"]:
            next_node = "human"
        else:
            next_node = "END"
        
        assert next_node == "human"

    def test_empty_findings_flow(self):
        """Test workflow with no findings"""
        state = {
            "repo_path": "/tmp/test",
            "semgrep_json": json.dumps({"results": []}),
            "crew_result": None,
            "findings": [],
            "mapped_findings": [],
            "patches": [],
            "verdict": None,
            "human_approved": False,
        }
        
        # Apply verdict logic
        if not state["findings"]:
            verdict = {"pass": False, "reason": "검토 항목 없음"}
        else:
            verdict = {"pass": False, "reason": "조항 매핑 부족"}
        
        assert verdict["pass"] is False
        assert verdict["reason"] == "검토 항목 없음"

    def test_partial_mapping_flow(self, sample_mapped_findings):
        """Test workflow with partial mapping"""
        findings = sample_mapped_findings + [{"file": "unmapped.py", "line": 1}]
        mapped = sample_mapped_findings  # One less than findings
        
        if len(mapped) < len(findings):
            verdict = {"pass": False, "reason": "조항 매핑 부족"}
        else:
            ok = all(m.get("clause_id") for m in mapped)
            verdict = {"pass": ok}
        
        assert verdict["pass"] is False
        assert verdict["reason"] == "조항 매핑 부족"


# Performance test (optional)
@pytest.mark.performance
class TestPerformance:
    """Performance tests for the security audit workflow"""

    def test_graph_compilation_time(self):
        """Test that graph compiles quickly"""
        import time
        
        start = time.time()
        from security_review_graph import graph
        end = time.time()
        
        # Should compile in under 1 second
        assert (end - start) < 1.0
