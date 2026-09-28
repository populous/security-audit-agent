# CMakeLists.txt
# CMake configuration for security-audit-agent

cmake_minimum_required(VERSION 3.20)
project(security-audit-agent VERSION 1.0.0 LANGUAGES NONE)

# Python 찾기
find_package(Python3 COMPONENTS Interpreter REQUIRED)

# Python 모듈 찾기 (pip 패키지)
include(cmake/FindPythonModules.cmake)

# 필수 Python 패키지 확인
find_python_module(langgraph REQUIRED)
find_python_module(crewai REQUIRED)
find_python_module(pytest REQUIRED)

# Semgrep 찾기 (옵션)
find_program(SEMGREP semgrep)
if(SEMGREP)
    message(STATUS "Semgrep found: ${SEMGREP}")
else()
    message(WARNING "Semgrep not found, security checks will be skipped")
endif()

# 테스트 활성화
enable_testing()

# CTest - pytest wrapping
add_test(
    NAME pytest_tests
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/run_pytest.py
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)

# Semgrep 보안 검사 (옵션)
if(SEMGREP)
    add_test(
        NAME semgrep_security_check
        COMMAND ${SEMGREP} --config=security-standards/ --error .
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    )
endif()

# CPack 설정
set(CPACK_PACKAGE_NAME "security-audit-agent")
set(CPACK_PACKAGE_VERSION "${PROJECT_VERSION}")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "LangGraph + CrewAI Security Audit Agent")
set(CPACK_PACKAGE_VENDOR "populous")
set(CPACK_PACKAGE_CONTACT "populous@empas.com")
set(CPACK_RESOURCE_FILE_README "${CMAKE_SOURCE_DIR}/README.md")

# Python 패키지 포함
set(CPACK_INSTALL_CMAKE_PROJECTS "")
set(CPACK_INSTALL_SCRIPTS "")

# 소스 파일 포함
set(CPACK_SOURCE_IGNORE_FILES
    ".git/"
    ".github/"
    "__pycache__/"
    "*.pyc"
    ".pytest_cache/"
    "build/"
    "dist/"
    ".venv/"
)

# 생성할 패키지 타입
set(CPACK_GENERATOR "TGZ;ZIP")

include(CPack)
