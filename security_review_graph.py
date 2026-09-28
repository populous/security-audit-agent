# security_review_graph.py
# LangGraph 플래너 + CrewAI 연동 보안 감사 워크플로

from typing import TypedDict, List, Optional, Any
from langgraph.graph import StateGraph, START, END
import subprocess, json, os
from crew_security_analysis import create_security_audit_crew

# 상태 정의
class ReviewState(TypedDict):
    repo_path: str
    semgrep_json: str               # Semgrep 원본 JSON (문자열)
    crew_result: Optional[dict]     # CrewAI kickoff 결과
    findings: List[dict]
    mapped_findings: List[dict]
    patches: List[dict]
    verdict: Optional[dict]
    human_approved: bool

# 1) Semgrep 실행 노드 (로컬)
def run_semgrep(state: ReviewState) -> ReviewState:
    repo = state["repo_path"]
    cmd = ["semgrep", "--config=security-standards/", "--json", repo]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    semgrep_json = result.stdout or "{}"
    return {**state, "semgrep_json": semgrep_json}

# 2) CrewAI 실행 노드 (크루 호출)
def run_crew_analysis(state: ReviewState) -> ReviewState:
    # SECURITY.md 요약은 RAG 에서 미리 가져온다고 가정 (또는 크루 내부에서 처리)
    security_md_summary = "SECURITY.md 요약 텍스트 (RAG 에서 조회)"

    crew = create_security_audit_crew()
    inputs = {
        "semgrep_json": state["semgrep_json"],
        "security_md_summary": security_md_summary,
        "findings": [],  # 첫 태스크에서 채움
    }
    raw_result = crew.kickoff(inputs=inputs)

    # raw_result 는 문자열/객체 혼합일 수 있으므로, 파싱 로직 필요
    # 여기서는 간단히 dict 로 가정 (실제 구현에서는 LLM 출력 파싱 추가)
    crew_result: dict = {
        "findings": [],          # static_task 출력
        "mapped_findings": [],   # rag_task 출력
        "patches": [],           # patch_task 출력
    }

    # 실제 구현: raw_result 를 structured output 으로 파싱
    # 예: crew_result["findings"] = parse_findings(raw_result)
    #     crew_result["mapped_findings"] = parse_mapped_findings(raw_result)
    #     crew_result["patches"] = parse_patches(raw_result)

    return {
        **state,
        "crew_result": crew_result,
        "findings": crew_result.get("findings", []),
        "mapped_findings": crew_result.get("mapped_findings", []),
        "patches": crew_result.get("patches", []),
    }

# 3) 판정자 (QMonad 스타일) 노드
def verdict_node(state: ReviewState) -> ReviewState:
    # 불변량: 모든 findings 에 clause_id 가 있는가?
    findings = state["findings"]
    mapped = state["mapped_findings"]

    if not findings:
        verdict = {"pass": False, "reason": "검토 항목 없음"}
    elif len(mapped) < len(findings):
        verdict = {"pass": False, "reason": "조항 매핑 부족"}
    else:
        ok = all(m.get("clause_id") and m["clause_id"] != "SEC-??" for m in mapped)
        verdict = {"pass": ok, "reason": "조항 매핑 완료" if ok else "조항 매핑 불완전"}

    return {**state, "verdict": verdict}

# 4) 인간 승인 대기 (HITL)
def wait_human_approval(state: ReviewState) -> ReviewState:
    # 외부 오케스트레이터가 state["patches"] 검토 후 human_approved=True 로 재진입
    return state

# 그래프 구성
builder = StateGraph(ReviewState)
builder.add_node("semgrep", run_semgrep)
builder.add_node("crew", run_crew_analysis)
builder.add_node("verdict", verdict_node)
builder.add_node("human", wait_human_approval)

builder.add_edge(START, "semgrep")
builder.add_edge("semgrep", "crew")
builder.add_edge("crew", "verdict")

# 분기: 판정 실패 → 종료, 성공 → 인간 대기
def route_after_verdict(state: ReviewState) -> str:
    if state["verdict"]["pass"]:
        return "human"
    return END

builder.add_conditional_edges("verdict", route_after_verdict)
builder.add_edge("human", END)

graph = builder.compile()

if __name__ == "__main__":
    # 테스트 실행
    initial_state = {
        "repo_path": "/path/to/your/repo",
        "semgrep_json": "",
        "crew_result": None,
        "findings": [],
        "mapped_findings": [],
        "patches": [],
        "verdict": None,
        "human_approved": False,
    }

    result = graph.invoke(initial_state)
    print("Verdict:", result["verdict"])
    print("Findings:", len(result["findings"]))
    print("Mapped findings:", len(result["mapped_findings"]))
    print("Patches:", len(result["patches"]))
