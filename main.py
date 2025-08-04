"""
HeartWings Lite
마음나래 Lite의 메인 진입점
"""

import sys, os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon
from utils.config_manager import is_password_set, check_password, set_password, get_font_size, get_school_year
from ui.dialogs import CreatePasswordDialog, PasswordDialog
from ui.main_window import MainApp

# 스크립트의 디렉토리를 sys.path에 추가하여 resources_rc를 찾을 수 있도록 합니다.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Qt 리소스 시스템을 임포트합니다.
# 이 파일은 pyside6-rcc resources.qrc -o resources_rc.py 명령으로 생성해야 합니다.
try:
    import resources_rc
except ImportError:
    print("오류: 'resources_rc.py' 파일을 찾을 수 없습니다.")
    print("스크립트와 같은 디렉토리에서 'pyside6-rcc resources.qrc -o resources_rc.py'를 실행했는지 확인하세요.")
    sys.exit(1)

# 테마 관리자 모듈을 가져옵니다.
from utils.theme_manager import ThemeManager

def main():
    """메인 애플리케이션 함수"""
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":icons/icon.png"))

    # --- 테마 관리자 초기화 ---
    font_size = get_font_size()
    theme_manager = ThemeManager(font_size=f"{font_size}px")
    theme_manager.apply_theme()

    # 학년도 초기화
    get_school_year()

    # 암호 설정 확인 및 처리
    if not is_password_set():
        dialog = CreatePasswordDialog()
        if dialog.exec():
            password = dialog.get_password()
            set_password(password)
        else:
            sys.exit(0)

    # 암호 확인
    while True:
        dialog = PasswordDialog()
        if dialog.exec():
            password = dialog.get_password()
            if check_password(password):
                # 데이터베이스 연결 확인은 이제 DatabaseWorker 내부에서 처리
                break
            else:
                QMessageBox.warning(None, '오류', '암호가 올바르지 않습니다.')
        else:
            sys.exit(0)

    # 메인 윈도우 실행
    main_window = MainApp(theme_manager)
    main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
