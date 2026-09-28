# crew_security_analysis.py
# CrewAI 보안 감사 실행 크루

from crewai import Agent, Task, Crew, Process, LLM
from typing import List, Dict, Any
import os

# LLM 설정 (로컬/원격 교체 가능)
llm = LLM(model=os.getenv("LLM_MODEL", "openai/gpt-5.2"))

# 1) 정적 검사 러너 (Semgrep 결과 파싱만, 실제 실행은 외부에서)
static_runner = Agent(
    role="Static Analysis Runner",
    goal="Semgrep JSON 결과를 보안 감사 항목으로 정리",
    backstory="보안 코딩 규격 기반 정적 검사 전문",
    llm=llm,
    allow_delegation=False,
)

# 2) RAG 조항 매퍼 (SECURITY.md 기반)
rag_mapper = Agent(
    role="RAG Clause Mapper",
    goal="각 findings 를 SECURITY.md 조항 (SEC-XX.X) 과 매핑",
    backstory="규격 문서 RAG 및 증거 매핑 전문",
    llm=llm,
    allow_delegation=False,
)

# 3) 패치 초안 작성자
patch_drafter = Agent(
    role="Patch Drafter",
    goal="매핑된 조항에 기반해 라인 단위 패치 초안 생성",
    backstory="보안 취약점 패치 전문",
    llm=llm,
    allow_delegation=False,
)

def create_security_audit_crew() -> Crew:
    """보안 감사용 CrewAI 크루 생성"""

    static_task = Task(
        description=(
            "다음 Semgrep JSON 결과를 보안 감사 항목으로 정리하세요.\n"
            "- 각 항목에 file, line, rule_id, message, severity 포함.\n"
            "Semgrep 결과:\n{semgrep_json}"
        ),
        expected_output=(
            "findings 리스트: [{file, line, rule_id, message, severity}, ...]"
        ),
        agent=static_runner,
    )

    rag_task = Task(
        description=(
            "정리된 findings 를 SECURITY.md 의 조항 (SEC-XX.X) 과 매핑하세요.\n"
            "- 각 findings 에 clause_id, evidence_required, fix_guidance 추가.\n"
            "SECURITY.md 요약:\n{security_md_summary}\n"
            "Findings:\n{findings}"
        ),
        expected_output=(
            "매핑된 findings 리스트: "
            "[{file, line, rule_id, message, severity, clause_id, evidence_required, fix_guidance}, ...]"
        ),
        agent=rag_mapper,
    )

    patch_task = Task(
        description=(
            "매핑된 findings 에 대해 라인 단위 패치 초안을 생성하세요.\n"
            "- 각 패치는 file, line, original_code, suggested_code, rationale 포함.\n"
            "Mapped findings:\n{mapped_findings}"
        ),
        expected_output=(
            "패치 초안 리스트: "
            "[{file, line, original_code, suggested_code, rationale}, ...]"
        ),
        agent=patch_drafter,
    )

    crew = Crew(
        agents=[static_runner, rag_mapper, patch_drafter],
        tasks=[static_task, rag_task, patch_task],
        process=Process.sequential,
        verbose=True,
    )
    return crew

if __name__ == "__main__":
    # 테스트 예시
    crew = create_security_audit_crew()
    
    test_semgrep_json = """
    {
        "results": [
            {
                "check_id": "sec-03-1-no-hardcoded-token",
                "path": "auth.py",
                "start": {"line": 42},
                "extra": {
                    "message": "인증 토큰이 소스코드에 하드코딩됨",
                    "metadata": {"severity": "ERROR"}
                }
            }
        ]
    }
    """
    
    inputs = {
        "semgrep_json": test_semgrep_json,
        "security_md_summary": "SEC-03.1: 인증 토큰은 평문 저장 금지",
        "findings": [],
    }
    
    result = crew.kickoff(inputs=inputs)
    print("Crew 결과:", result)
