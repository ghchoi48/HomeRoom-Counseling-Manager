"""
공통으로 사용되는 헬퍼 함수들을 모아놓은 모듈
"""

import os
import sys

def get_base_dir():
    """
    실행 파일의 기본 디렉토리를 반환합니다.
    PyInstaller 등으로 패키징되었을 때와 일반 파이썬 환경 모두에서 작동합니다.
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller에 의해 생성된 임시 폴더의 경로
        return os.path.dirname(sys.executable)
    else:
        # 일반적인 .py 파일 실행 환경
        # 이 파일(helpers.py)의 위치는 /utils/ 이므로, 상위 디렉토리를 반환해야 함
        return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
