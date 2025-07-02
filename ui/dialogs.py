"""
다이얼로그 클래스들 모듈
암호 관련 다이얼로그와 상담 기록 수정 다이얼로그를 포함합니다.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QDialogButtonBox,
    QLineEdit, QComboBox, QDateTimeEdit, QTextEdit, QMessageBox
)
from PySide6.QtCore import QDateTime


class PasswordDialogBase(QDialog):
    """암호 다이얼로그의 기본 클래스"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.buttons)


class CreatePasswordDialog(PasswordDialogBase):
    """새 암호 생성 다이얼로그"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('새 암호 생성')
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.Password)
        
        self.form_layout.addRow('새 암호:', self.password_edit)
        self.form_layout.addRow('암호 확인:', self.confirm_edit)

    def accept(self):
        if self.password_edit.text() == self.confirm_edit.text():
            if len(self.password_edit.text()) < 4:
                QMessageBox.warning(self, '오류', '암호는 4자 이상이어야 합니다.')
                return
            super().accept()
        else:
            QMessageBox.warning(self, '오류', '암호가 일치하지 않습니다.')

    def get_password(self):
        return self.password_edit.text()


class PasswordDialog(PasswordDialogBase):
    """암호 입력 다이얼로그"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('암호 입력')
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.form_layout.addRow('암호:', self.password_edit)

    def get_password(self):
        return self.password_edit.text()


class ChangePasswordDialog(PasswordDialogBase):
    """암호 변경 다이얼로그"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('암호 변경')
        self.old_password_edit = QLineEdit()
        self.old_password_edit.setEchoMode(QLineEdit.Password)
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.Password)

        self.form_layout.addRow('기존 암호:', self.old_password_edit)
        self.form_layout.addRow('새 암호:', self.new_password_edit)
        self.form_layout.addRow('새 암호 확인:', self.confirm_edit)

    def accept(self):
        if self.new_password_edit.text() == self.confirm_edit.text():
            if len(self.new_password_edit.text()) < 4:
                QMessageBox.warning(self, '오류', '새 암호는 4자 이상이어야 합니다.')
                return
            super().accept()
        else:
            QMessageBox.warning(self, '오류', '새 암호가 일치하지 않습니다.')

    def get_passwords(self):
        return (
            self.old_password_edit.text(),
            self.new_password_edit.text()
        )


class EditCounselDialog(QDialog):
    """상담 기록 수정 다이얼로그"""
    def __init__(self, record, parent=None):
        super().__init__(parent)
        self.setWindowTitle('상담기록 수정')

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setDateTime(QDateTime.fromString(record['일시'], "yyyy-MM-dd HH:mm"))
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.datetime_edit.setCalendarPopup(True)

        self.target_combo = QComboBox()
        self.target_combo.setEditable(True)
        self.target_combo.setMinimumWidth(200)
        self.target_combo.addItems(['학생 본인', '보호자', '친구', '기타'])
        self.target_combo.setCurrentText(record['대상'])

        self.method_combo = QComboBox()
        self.method_combo.setEditable(True)
        self.method_combo.setMinimumWidth(200)
        self.method_combo.addItems(['대면', '전화', '온라인'])
        self.method_combo.setCurrentText(record['방법'])

        self.counsel_input = QTextEdit()
        self.counsel_input.setText(record['내용'])
        
        form_layout.addRow('상담 일시', self.datetime_edit)
        form_layout.addRow('상담 대상', self.target_combo)
        form_layout.addRow('상담 방법', self.method_combo)
        form_layout.addRow('상담 내용', self.counsel_input)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout.addLayout(form_layout)
        layout.addWidget(self.buttons)

    def get_data(self):
        return {
            '일시': self.datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm"),
            '대상': self.target_combo.currentText(),
            '방법': self.method_combo.currentText(),
            '내용': self.counsel_input.toPlainText().strip()
        } 