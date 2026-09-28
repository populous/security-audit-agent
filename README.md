# 보안 감사 리뷰 에이전트 (LangGraph + CrewAI)

CMake 기반 빌드 시스템을 지원하는 보안 감사 리뷰 에이전트입니다.

## 빠른 시작

### 1. 의존성 설치

```bash
pip install langgraph crewai semgrep pytest
```

### 2. CMake 설정

```bash
# CMake configure
cmake --preset=default

# CMake build
cmake --build --preset=default-build

# CTest 실행
cmake --build --preset=default-test

# 또는 직접 실행
ctest --preset=default-test --output-on-failure
```

### 3. 수동 테스트

```bash
# pytest 직접 실행
pytest tests/ -v

# Semgrep 보안 검사
semgrep --config=security-standards/ --error .
```

## 프로젝트 구조

```
security-audit-agent/
  ├─ src/                          # 소스 코드
  │  ├─ security_review_graph.py   # LangGraph 플래너
  │  ├─ crew_security_analysis.py  # CrewAI 실행 크루
  │  └─ run_audit.py               # 실행 스크립트
  ├─ tests/                        # 테스트
  │  ├─ test_security_review.py
  │  ├─ test_crew_analysis.py
  │  ├─ test_end_to_end.py
  │  └─ conftest.py
  ├─ security-standards/           # Semgrep 규칙
  │  └─ sec-03-1.yml
  ├─ SECURITY.md                   # 보안 규격 명세
  ├─ CMakeLists.txt                # CMake 설정
  ├─ CMakePresets.json             # CMake 프리셋
  ├─ cmake/                        # CMake 모듈
  │  └─ FindPythonModules.cmake
  ├─ scripts/                      # 보조 스크립트
  │  └─ run_pytest.py
  └─ README.md
```

## CTest 사용법

### 테스트 실행

```bash
# 모든 테스트
ctest

# 상세 출력
ctest --output-on-failure

# 특정 테스트만
ctest -R pytest_tests

# Semgrep 테스트만
ctest -R semgrep
```

### CMake 프리셋

```bash
# Debug 빌드
cmake --preset=debug
cmake --build --preset=debug-build

# CI 빌드
cmake --preset=ci
cmake --build --preset=ci-build
```

## CPack 패키징

```bash
# 패키지 생성
ccpack -G TGZ

# 생성된 파일
security-audit-agent-1.0.0-Linux.tar.gz
```

## GitHub Actions

PR 또는 main 브랜치 푸시 시 자동 실행:
- CMake configure/build
- CTest 실행
- Semgrep 보안 검사
- CPack 패키징
- 아티팩트 업로드

## 라이선스

MIT
