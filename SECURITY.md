# 보안 코딩 규격 (SECURITY.md)

## [SEC-03.1] 인증 토큰 저장

- **요구사항**:
  - 인증 토큰은 절대 파일/로그/환경변수에 평문으로 저장하지 않는다.
  - 모든 토큰 접근은 인가 체크를 거친다.
  
- **증거 요구사항**:
  - 토큰 사용 지점에서 인가 미들웨어 호출 증거.
  - 토큰 로딩 함수가 암호화 저장소에서 읽는 증거.
  
- **관련 규칙**:
  - semgrep: `python.lang.security.audit.detect-hardcoded-token`
  - semgrep: `qlang.security.no-plaintext-token-in-env`

---

## [SEC-04.2] SQL 인젝션 방지

- **요구사항**:
  - 모든 데이터베이스 쿼리는 파라미터화된 쿼리 또는 ORM 을 사용한다.
  - 문자열 연결을 통한 동적 쿼리 생성을 금지한다.
  
- **증거 요구사항**:
  - 쿼리 실행 지점에서 파라미터 바인딩 사용 증거.
  - 동적 쿼리 생성 시 이스케이프 함수 호출 증거.
  
- **관련 규칙**:
  - semgrep: `python.lang.security.audit.sql-injection`
  - semgrep: `qlang.security.no-string-concat-query`

---

## [SEC-05.3] 암호화 키 관리

- **요구사항**:
  - 암호화 키는 시크릿 관리 시스템 (Vault, AWS Secrets Manager 등) 에서 관리한다.
  - 소스코드/설정 파일에 하드코딩 금지.
  
- **증거 요구사항**:
  - 키 로딩 시 시크릿 관리 시스템 API 호출 증거.
  - 환경변수 직접 읽기 없음.
  
- **관련 규칙**:
  - semgrep: `python.lang.security.audit.hardcoded-encryption-key`
  - semgrep: `qlang.security.no-hardcoded-secrets`

---

## [SEC-06.1] 로그 민감정보 필터링

- **요구사항**:
  - 로그에 비밀번호, 토큰, PII(개인식별정보) 를 기록하지 않는다.
  - 모든 로그 출력 전 필터링 함수를 거친다.
  
- **증거 요구사항**:
  - 로그 호출 시 마스킹/필터링 함수 사용 증거.
  - 민감정보 패턴 탐지 규칙 통과.
  
- **관련 규칙**:
  - semgrep: `python.lang.security.audit.potential-sensitive-info-leak`
  - semgrep: `qlang.security.no-sensitive-data-in-logs`

---

## 검사 및 검증 워크플로

1. **정적 검사**: Semgrep 규칙 실행 (`security-standards/` 디렉토리)
2. **LLM 리뷰**: 규정 조항 매핑 및 패치 초안 생성
3. **판정자 검증**: 증거 충분성, 조항 매핑 일관성 확인
4. **인간 검토**: 패치 승인 및 머지

---

## 버전

- **버전**: 1.0.0
- **최종 수정일**: 2026-09-28
- **적용 범위**: 모든 Python 기반 서비스
