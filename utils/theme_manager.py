import darkdetect
from PySide6.QtCore import QFile, QTextStream, QIODevice
from PySide6.QtWidgets import QApplication

# theme.py에서 색상 팔레트를 가져옵니다.
# main.py에서 프로젝트 루트를 sys.path에 추가하므로 이 경로가 동작합니다.
from ui.theme import PALETTE_LIGHT, PALETTE_DARK


class ThemeManager:
    """애플리케이션의 테마(라이트/다크)를 관리하는 클래스."""

    def __init__(self):
        """ThemeManager를 초기화합니다."""
        self.is_dark_mode = (darkdetect.theme() == "Dark")
        self.base_style = self._load_stylesheet_from_resource()

    def _load_stylesheet_from_resource(self):
        """Qt 리소스 시스템에서 base.qss 파일을 안전하게 로드합니다."""
        qss_file = QFile(":/ui/base.qss")
        if not qss_file.open(QIODevice.ReadOnly | QIODevice.Text):
            print("기본 스타일시트 'base.qss'를 리소스에서 찾거나 열 수 없습니다.")
            return ""
        stream = QTextStream(qss_file)
        return stream.readAll()

    def _create_stylesheet(self, palette):
        """주어진 팔레트를 사용하여 QSS를 동적으로 생성합니다."""
        stylesheet = self.base_style
        # 팔레트의 값을 스타일시트의 플레이스홀더에 적용합니다.
        for key, value in palette.items():
            stylesheet = stylesheet.replace(f"{{{{{key}}}}}", value)
        return stylesheet

    def apply_theme(self):
        """현재 테마 설정에 따라 스타일시트를 적용합니다."""
        palette = PALETTE_DARK if self.is_dark_mode else PALETTE_LIGHT
        stylesheet = self._create_stylesheet(palette)
        QApplication.instance().setStyleSheet(stylesheet)

    def toggle_theme(self):
        """테마를 전환하고 변경사항을 적용합니다."""
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def get_theme_icon_path(self):
        """현재 테마에 맞는 아이콘의 리소스 경로를 반환합니다."""
        return ":/icons/moon.png" if self.is_dark_mode else ":/icons/sun.png"

