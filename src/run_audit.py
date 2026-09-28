#!/usr/bin/env python3
# src/run_audit.py
# 보안 감사 워크플로 실행 예시

from security_review_graph import graph

def main():
    initial_state = {
        "repo_path": "/path/to/your/repo",  # 실제 레포지토리 경로로 수정
        "semgrep_json": "",
        "crew_result": None,
        "findings": [],
        "mapped_findings": [],
        "patches": [],
        "verdict": None,
        "human_approved": False,
    }

    print("보안 감사 워크플로 실행 중...")
    result = graph.invoke(initial_state)
    
    print("\n=== 감사 결과 ===")
    print("판정:", result["verdict"])
    print("발견된 항목:", len(result["findings"]))
    print("규정 매핑 완료:", len(result["mapped_findings"]))
    print("패치 초안:", len(result["patches"]))
    
    if result["verdict"]["pass"]:
        print("\n✓ 규정 준수 검증 완료. 패치 검토 대기 중...")
    else:
        print(f"\n✗ 검증 실패: {result['verdict']['reason']}")

if __name__ == "__main__":
    main()
