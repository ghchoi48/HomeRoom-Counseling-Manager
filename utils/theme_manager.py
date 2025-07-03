# 테마 관리 모듈

import darkdetect
from ui.styles import light_qss, dark_qss


def get_current_theme():
    # 현재 시스템 테마를 감지하여 반환

    return 'dark' if darkdetect.isDark() else 'light'


def get_stylesheet():
    # 현재 시스템 테마에 맞는 앱 테마 반환

    if get_current_theme() == 'dark':
        return dark_qss
    else:
        return light_qss


def apply_theme_to_app(app):
    # 앱에 반환된 테마 적용
    app.setStyleSheet(get_stylesheet()) 