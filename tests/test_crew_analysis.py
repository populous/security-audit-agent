# tests/test_crew_analysis.py
# Tests for CrewAI security analysis crew

import pytest
import json
from crew_security_analysis import create_security_audit_crew, static_runner, rag_mapper, patch_drafter


class TestCrewAICrew:
    """Tests for CrewAI security analysis crew"""

    def test_crew_creation(self):
        """Test that crew is created successfully"""
        crew = create_security_audit_crew()
        
        assert crew is not None
        assert len(crew.agents) == 3
        assert len(crew.tasks) == 3
        
        # Check agent roles
        roles = [agent.role for agent in crew.agents]
        assert "Static Analysis Runner" in roles
        assert "RAG Clause Mapper" in roles
        assert "Patch Drafter" in roles

    def test_agents_configuration(self):
        """Test that agents are configured correctly"""
        # Check static_runner
        assert static_runner.role == "Static Analysis Runner"
        assert static_runner.allow_delegation is False
        
        # Check rag_mapper
        assert rag_mapper.role == "RAG Clause Mapper"
        assert rag_mapper.allow_delegation is False
        
        # Check patch_drafter
        assert patch_drafter.role == "Patch Drafter"
        assert patch_drafter.allow_delegation is False

    def test_tasks_configuration(self):
        """Test that tasks are configured correctly"""
        crew = create_security_audit_crew()
        
        # Check task descriptions
        task_descriptions = [task.description for task in crew.tasks]
        
        assert any("Semgrep JSON" in desc for desc in task_descriptions)
        assert any("SECURITY.md" in desc for desc in task_descriptions)
        assert any("패치 초안" in desc for desc in task_descriptions)

    def test_semgrep_parsing_logic(self, sample_semgrep_json):
        """Test Semgrep JSON parsing logic (mock)"""
        # Mock parsing logic that would be in static_runner task
        data = json.loads(sample_semgrep_json)
        findings = []
        
        for result in data.get("results", []):
            findings.append({
                "file": result.get("path"),
                "line": result.get("start", {}).get("line"),
                "rule_id": result.get("check_id"),
                "message": result.get("extra", {}).get("message", ""),
                "severity": result.get("extra", {}).get("metadata", {}).get("severity", "medium")
            })
        
        assert len(findings) == 2
        assert findings[0]["file"] == "auth.py"
        assert findings[0]["line"] == 42
        assert findings[0]["rule_id"] == "sec-03-1-no-hardcoded-token"
        assert findings[0]["severity"] == "ERROR"

    def test_clause_mapping_logic(self, sample_mapped_findings):
        """Test clause mapping logic (mock)"""
        # Verify all findings have clause_id
        for finding in sample_mapped_findings:
            assert "clause_id" in finding
            assert finding["clause_id"] is not None
            assert finding["clause_id"] != "SEC-??"
            assert finding["clause_id"].startswith("SEC-")

    def test_patch_structure(self, sample_patches):
        """Test patch draft structure"""
        for patch in sample_patches:
            assert "file" in patch
            assert "line" in patch
            assert "original_code" in patch
            assert "suggested_code" in patch
            assert "rationale" in patch
            
            # Verify rationale mentions SEC clause
            assert "SEC-" in patch["rationale"]

    def test_evidence_requirements(self, sample_mapped_findings):
        """Test that evidence requirements are present"""
        for finding in sample_mapped_findings:
            assert "evidence_required" in finding
            assert isinstance(finding["evidence_required"], list)
            assert len(finding["evidence_required"]) > 0

    def test_fix_guidance(self, sample_mapped_findings):
        """Test that fix guidance is present"""
        for finding in sample_mapped_findings:
            assert "fix_guidance" in finding
            assert isinstance(finding["fix_guidance"], str)
            assert len(finding["fix_guidance"]) > 0


# Integration test (requires actual LLM, skip in CI)
@pytest.mark.skip(reason="Requires actual LLM API call")
class TestCrewIntegration:
    """Integration tests for CrewAI crew (requires LLM)"""

    def test_full_crew_execution(self, sample_semgrep_json, sample_security_md_summary):
        """Test full crew execution with real LLM"""
        crew = create_security_audit_crew()
        
        inputs = {
            "semgrep_json": sample_semgrep_json,
            "security_md_summary": sample_security_md_summary,
            "findings": [],
        }
        
        result = crew.kickoff(inputs=inputs)
        
        assert result is not None
        # Further assertions depend on actual LLM output format
