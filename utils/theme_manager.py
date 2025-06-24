"""
테마 관리 모듈
시스템 테마 감지 및 스타일시트 적용 기능을 포함합니다.
"""

import darkdetect
from ui.styles import light_qss, dark_qss


def get_current_theme():
    """현재 시스템 테마를 감지하여 반환합니다."""
    return 'dark' if darkdetect.isDark() else 'light'


def get_stylesheet():
    """현재 테마에 맞는 스타일시트를 반환합니다."""
    if get_current_theme() == 'dark':
        return dark_qss
    else:
        return light_qss


def apply_theme_to_app(app):
    """애플리케이션에 현재 테마를 적용합니다."""
    app.setStyleSheet(get_stylesheet()) 