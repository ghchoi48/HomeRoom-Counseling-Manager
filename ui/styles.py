"""
스타일시트 정의 모듈
앤트 디자인 기반의 라이트/다크 테마 스타일을 포함합니다.
"""

light_qss = '''
/* Ant Design - Light Theme */
QWidget {
    background-color: #f0f2f5;
    color: rgba(0, 0, 0, 0.85);
    font-size: 14px;
}
QMainWindow, QDialog {
    background-color: #f0f2f5;
}
QLabel {
    background-color: transparent;
}
QLineEdit, QComboBox, QDateTimeEdit, QTextEdit {
    background-color: #ffffff;
    border: 1px solid #d9d9d9;
    border-radius: 2px;
    padding: 8px;
}
QLineEdit:focus, QComboBox:focus, QDateTimeEdit:focus, QTextEdit:focus {
    border-color: #40a9ff;
}
QListWidget {
    background-color: #ffffff;
    border: 1px solid #d9d9d9;
    border-radius: 2px;
}
QListWidget::item {
    padding: 8px 12px;
}
QListWidget::item:hover {
    background-color: #e6f7ff;
}
QListWidget::item:selected {
    background-color: #bae7ff;
    color: rgba(0, 0, 0, 0.85);
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: rgba(0, 0, 0, 0.85);
    border: 1px solid #d9d9d9;
    border-radius: 2px;
    padding: 4px;
    outline: 0px;
}
QComboBox QAbstractItemView::item {
    padding: 8px 12px;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #e6f7ff;
}
QComboBox QAbstractItemView::item:selected {
    background-color: #1890ff;
    color: #ffffff;
}
QPushButton {
    background-color: #1890ff;
    color: #ffffff;
    border: 1px solid #1890ff;
    border-radius: 2px;
    padding: 8px 15px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #40a9ff;
    border-color: #40a9ff;
}
QPushButton:pressed {
    background-color: #096dd9;
    border-color: #096dd9;
}
QTabWidget::pane {
    border-top: 1px solid #f0f0f0;
}
QTabBar::tab {
    background: transparent;
    color: rgba(0, 0, 0, 0.85);
    border: none;
    border-bottom: 2px solid transparent;
    padding: 10px 16px;
    margin-right: 16px;
}
QTabBar::tab:hover {
    color: #40a9ff;
}
QTabBar::tab:selected {
    color: #096dd9;
    border-bottom: 2px solid #096dd9;
}
'''

dark_qss = '''
/* Ant Design - Dark Theme */
QWidget {
    background-color: #1f1f1f;
    color: rgba(255, 255, 255, 0.85);
    font-size: 14px;
}
QMainWindow, QDialog {
    background-color: #1f1f1f;
}
QLabel {
    background-color: transparent;
}
QLineEdit, QComboBox, QDateTimeEdit, QTextEdit {
    background-color: #141414;
    border: 1px solid #434343;
    border-radius: 2px;
    padding: 8px;
}
QLineEdit:focus, QComboBox:focus, QDateTimeEdit:focus, QTextEdit:focus {
    border-color: #096dd9;
}
QListWidget {
    background-color: #141414;
    border: 1px solid #434343;
    border-radius: 2px;
}
QListWidget::item {
    padding: 8px 12px;
}
QListWidget::item:hover {
    background-color: #2a2a2a;
}
QListWidget::item:selected {
    background-color: #112a45;
    color: rgba(255, 255, 255, 0.85);
}
QComboBox QAbstractItemView {
    background-color: #141414;
    color: rgba(255, 255, 255, 0.85);
    border: 1px solid #434343;
    border-radius: 2px;
    padding: 4px;
    outline: 0px;
}
QComboBox QAbstractItemView::item {
    padding: 8px 12px;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #2a2a2a;
}
QComboBox QAbstractItemView::item:selected {
    background-color: #177ddc;
    color: #ffffff;
}
QPushButton {
    background-color: #096dd9;
    color: #ffffff;
    border: 1px solid #096dd9;
    border-radius: 2px;
    padding: 8px 15px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #177ddc;
    border-color: #177ddc;
}
QPushButton:pressed {
    background-color: #0050b3;
    border-color: #0050b3;
}
QTabWidget::pane {
    border-top: 1px solid #303030;
}
QTabBar::tab {
    background: transparent;
    color: rgba(255, 255, 255, 0.85);
    border: none;
    border-bottom: 2px solid transparent;
    padding: 10px 16px;
    margin-right: 16px;
}
QTabBar::tab:hover {
    color: #177ddc;
}
QTabBar::tab:selected {
    color: #096dd9;
    border-bottom: 2px solid #096dd9;
}
''' 