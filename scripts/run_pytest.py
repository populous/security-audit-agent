#!/usr/bin/env python3
# scripts/run_pytest.py
# Pytest wrapper for CTest

import subprocess
import sys
import os

def main():
    # 프로젝트 루트 디렉토리로 이동
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    os.chdir(root_dir)

    # PYTHONPATH 에 src 디렉토리 추가
    src_dir = os.path.join(root_dir, "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    # pytest 실행
    pytest_args = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "-m",
        "not performance"  # 성능 테스트 제외
    ]

    print(f"Running pytest from: {root_dir}")
    print(f"PYTHONPATH: {src_dir}")
    print(f"Command: {' '.join(pytest_args)}")

    result = subprocess.run(pytest_args)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
