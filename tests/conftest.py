# tests/conftest.py
# Pytest fixtures for security audit tests

import pytest
import json


@pytest.fixture
def sample_semgrep_result():
    """Sample Semgrep JSON result for testing"""
    return {
        "results": [
            {
                "check_id": "sec-03-1-no-hardcoded-token",
                "path": "auth.py",
                "start": {"line": 42, "col": 1},
                "end": {"line": 42, "col": 20},
                "extra": {
                    "message": "인증 토큰이 소스코드에 하드코딩됨 (SEC-03.1 위반)",
                    "metadata": {
                        "severity": "ERROR",
                        "clause_id": "SEC-03.1"
                    }
                }
            },
            {
                "check_id": "sec-03-1-no-token-in-env",
                "path": "config.py",
                "start": {"line": 15, "col": 1},
                "end": {"line": 15, "col": 30},
                "extra": {
                    "message": "민감정보가 환경변수에 평문으로 저장됨 (SEC-03.1 위반)",
                    "metadata": {
                        "severity": "WARNING",
                        "clause_id": "SEC-03.1"
                    }
                }
            }
        ]
    }


@pytest.fixture
def sample_semgrep_json(sample_semgrep_result):
    """Sample Semgrep result as JSON string"""
    return json.dumps(sample_semgrep_result)


@pytest.fixture
def sample_security_md_summary():
    """Sample SECURITY.md summary for RAG"""
    return """
    ## [SEC-03.1] 인증 토큰 저장
    - 요구사항: 인증 토큰은 절대 파일/로그/환경변수에 평문으로 저장하지 않는다.
    - 증거 요구사항: 토큰 사용 지점에서 인가 미들웨어 호출 증거.
    - 관련 규칙: semgrep: python.lang.security.audit.detect-hardcoded-token
    
    ## [SEC-04.2] SQL 인젝션 방지
    - 요구사항: 모든 데이터베이스 쿼리는 파라미터화된 쿼리 또는 ORM 을 사용한다.
    - 관련 규칙: semgrep: python.lang.security.audit.sql-injection
    """


@pytest.fixture
def sample_mapped_findings():
    """Sample mapped findings with clause_id"""
    return [
        {
            "file": "auth.py",
            "line": 42,
            "rule_id": "sec-03-1-no-hardcoded-token",
            "message": "인증 토큰이 소스코드에 하드코딩됨",
            "severity": "ERROR",
            "clause_id": "SEC-03.1",
            "evidence_required": ["인가 미들웨어 호출", "암호화 저장소 사용"],
            "fix_guidance": "환경변수/시크릿 관리 시스템으로 이동"
        },
        {
            "file": "config.py",
            "line": 15,
            "rule_id": "sec-03-1-no-token-in-env",
            "message": "민감정보가 환경변수에 평문으로 저장됨",
            "severity": "WARNING",
            "clause_id": "SEC-03.1",
            "evidence_required": ["시크릿 관리 시스템 사용 여부 확인"],
            "fix_guidance": "Vault, AWS Secrets Manager 등 시크릿 관리 시스템 사용"
        }
    ]


@pytest.fixture
def sample_patches():
    """Sample patch drafts"""
    return [
        {
            "file": "auth.py",
            "line": 42,
            "original_code": 'TOKEN = "hardcoded_secret_123"',
            "suggested_code": 'TOKEN = os.getenv("AUTH_TOKEN")',
            "rationale": "하드코딩된 토큰을 환경변수로 이동 (SEC-03.1 준수)"
        }
    ]


@pytest.fixture
def initial_review_state():
    """Initial state for ReviewState graph"""
    return {
        "repo_path": "/tmp/test-repo",
        "semgrep_json": "",
        "crew_result": None,
        "findings": [],
        "mapped_findings": [],
        "patches": [],
        "verdict": None,
        "human_approved": False,
    }
