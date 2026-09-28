# 보안 감사 리뷰 에이전트 (LangGraph + CrewAI)

## 개요

이 프로젝트는 **보안 코딩 규격 (SECURITY.md)** 을 기준으로 코드를 자동으로 감사하는 멀티에이전트 시스템입니다.

- **LangGraph**: 워크플로 오케스트레이션 (분기, 검증, HITL)
- **CrewAI**: 정적 검사, RAG 매핑, 패치 생성 실행
- **Semgrep**: 규칙 기반 정적 분석
- **QMonad 스타일 판정자**: 규정 준수 불변량 검증

## 파일 구조

```
security-audit-agent/
  ├─ security_review_graph.py      # LangGraph 플래너
  ├─ crew_security_analysis.py     # CrewAI 실행 크루
  ├─ run_audit.py                  # 실행 예시
  ├─ SECURITY.md                   # 보안 규격 명세
  ├─ security-standards/
  │   └─ sec-03-1.yml              # Semgrep 규칙 (SEC-03.1)
  └─ README.md                     # 이 파일
```

## 설치 및 설정

### 1. 의존성 설치

```bash
pip install langgraph crewai semgrep
```

### 2. 환경 변수 설정

```bash
export LLM_MODEL="openai/gpt-5.2"  # 또는 로컬 LLM
```

### 3. Semgrep 규칙 배치

`security-standards/` 디렉토리에 `.yml` 규칙 파일들을 배치합니다.

## 실행 방법

```bash
python run_audit.py
```

`run_audit.py` 내부의 `repo_path` 를 실제 레포지토리 경로로 수정하세요.

## 워크플로

1. **Semgrep 실행**: `security-standards/` 규칙으로 정적 검사
2. **CrewAI 분석**:
   - 정적 결과 정리
   - SECURITY.md 조항 매핑 (RAG)
   - 패치 초안 생성
3. **판정자 검증**: 모든 findings 에 clause_id 매핑 여부 확인
4. **인간 검토**: 패치 승인 후 머지

## 규격 확장 방법

### SECURITY.md 에 새 조항 추가

```markdown
## [SEC-XX.X] 조항 제목

- **요구사항**: ...
- **증거 요구사항**: ...
- **관련 규칙**: ...
```

### Semgrep 규칙 추가

`security-standards/sec-xx-x.yml` 파일에 규칙 추가:

```yaml
rules:
  - id: sec-xx-x-rule-name
    patterns: [...]
    message: "위반 메시지"
    languages: [python]
    severity: ERROR
    metadata:
      clause_id: "SEC-XX.X"
      evidence_required: [...]
      fix_guidance: "..."
```

## 아키텍처 (QLang/QMonad 관점)

- **CrewAI 노드**: 계산층 (정적 결과 → 매핑 → 패치)
- **LangGraph 플래너**: 위상층 (규정 준수 분기, HITL, 검증)
- **판정자 (verdict_node)**: QMonad 스타일 공통 문맥 (불변량 검증)

## 다음 단계

- RAG 인덱스 구축 (SECURITY.md 벡터화)
- GitHub Actions 연동 (PR 코멘트 자동 생성)
- 패치 자동 PR 생성

---

**버전**: 1.0.0  
**생성일**: 2026-09-28
