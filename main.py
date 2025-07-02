"""
HomeRoom Counseling Manager
담임교사용 상담일지 프로그램의 메인 진입점
"""

import sys
import threading
from PySide6.QtWidgets import QApplication, QMessageBox

from database import Database
from utils.config_manager import is_password_set, check_password, set_password
from utils.theme_manager import apply_theme_to_app
from ui.dialogs import CreatePasswordDialog, PasswordDialog
from ui.main_window import MainApp
from utils.updater import check_for_updates


def main():
    """메인 애플리케이션 함수"""
    app = QApplication(sys.argv)
    
    # 테마 적용
    apply_theme_to_app(app)

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
                db = Database()
                if db.check_connection():
                    break
                else:
                    QMessageBox.critical(None, '오류', '데이터베이스에 연결할 수 없습니다.')
                    sys.exit(1)
            else:
                QMessageBox.warning(None, '오류', '암호가 올바르지 않습니다.')
        else:
            sys.exit(0)

    # 메인 윈도우 실행
    if db:
        main_window = MainApp(db)
        main_window.show()
        # 백그라운드에서 업데이트 확인
        update_thread = threading.Thread(target=check_for_updates, args=(main_window,))
        update_thread.start()
        sys.exit(app.exec())


if __name__ == '__main__':
    main()
