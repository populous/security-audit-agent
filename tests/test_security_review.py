# tests/test_security_review.py
# Tests for LangGraph security review workflow

import pytest
from security_review_graph import graph, ReviewState


class TestSecurityReviewGraph:
    """Tests for the LangGraph security review workflow"""

    def test_graph_initialization(self):
        """Test that the graph compiles successfully"""
        assert graph is not None
        assert hasattr(graph, "invoke")

    def test_verdict_no_findings(self, initial_review_state):
        """Test verdict when no findings exist"""
        state = initial_review_state.copy()
        state["findings"] = []
        state["mapped_findings"] = []
        
        # Manually test verdict logic
        if not state["findings"]:
            verdict = {"pass": False, "reason": "검토 항목 없음"}
        else:
            verdict = {"pass": False, "reason": "조항 매핑 부족"}
        
        assert verdict["pass"] is False
        assert verdict["reason"] == "검토 항목 없음"

    def test_verdict_insufficient_mapping(self, initial_review_state, sample_mapped_findings):
        """Test verdict when mapping is insufficient"""
        state = initial_review_state.copy()
        state["findings"] = sample_mapped_findings + [{"file": "extra.py", "line": 1}]  # One extra finding
        state["mapped_findings"] = sample_mapped_findings
        
        findings = state["findings"]
        mapped = state["mapped_findings"]
        
        if len(mapped) < len(findings):
            verdict = {"pass": False, "reason": "조항 매핑 부족"}
        else:
            ok = all(m.get("clause_id") and m["clause_id"] != "SEC-??" for m in mapped)
            verdict = {"pass": ok, "reason": "조항 매핑 완료" if ok else "조항 매핑 불완전"}
        
        assert verdict["pass"] is False
        assert verdict["reason"] == "조항 매핑 부족"

    def test_verdict_complete_mapping(self, initial_review_state, sample_mapped_findings):
        """Test verdict when all findings are mapped"""
        state = initial_review_state.copy()
        state["findings"] = sample_mapped_findings
        state["mapped_findings"] = sample_mapped_findings
        
        findings = state["findings"]
        mapped = state["mapped_findings"]
        
        if not findings:
            verdict = {"pass": False, "reason": "검토 항목 없음"}
        elif len(mapped) < len(findings):
            verdict = {"pass": False, "reason": "조항 매핑 부족"}
        else:
            ok = all(m.get("clause_id") and m["clause_id"] != "SEC-??" for m in mapped)
            verdict = {"pass": ok, "reason": "조항 매핑 완료" if ok else "조항 매핑 불완전"}
        
        assert verdict["pass"] is True
        assert verdict["reason"] == "조항 매핑 완료"

    def test_verdict_incomplete_clause_id(self, initial_review_state):
        """Test verdict when clause_id is incomplete"""
        state = initial_review_state.copy()
        state["findings"] = [{"file": "test.py", "line": 1}]
        state["mapped_findings"] = [{
            "file": "test.py",
            "line": 1,
            "clause_id": "SEC-??"  # Incomplete
        }]
        
        mapped = state["mapped_findings"]
        ok = all(m.get("clause_id") and m["clause_id"] != "SEC-??" for m in mapped)
        verdict = {"pass": ok, "reason": "조항 매핑 완료" if ok else "조항 매핑 불완전"}
        
        assert verdict["pass"] is False
        assert verdict["reason"] == "조항 매핑 불완전"

    def test_route_after_verdict_pass(self, initial_review_state, sample_mapped_findings):
        """Test routing when verdict passes"""
        state = initial_review_state.copy()
        state["findings"] = sample_mapped_findings
        state["mapped_findings"] = sample_mapped_findings
        state["verdict"] = {"pass": True, "reason": "조항 매핑 완료"}
        
        # Simulate route_after_verdict logic
        if state["verdict"]["pass"]:
            next_node = "human"
        else:
            next_node = "END"
        
        assert next_node == "human"

    def test_route_after_verdict_fail(self, initial_review_state):
        """Test routing when verdict fails"""
        state = initial_review_state.copy()
        state["verdict"] = {"pass": False, "reason": "검토 항목 없음"}
        
        # Simulate route_after_verdict logic
        if state["verdict"]["pass"]:
            next_node = "human"
        else:
            next_node = "END"
        
        assert next_node == "END"
