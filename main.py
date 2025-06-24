from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QTextEdit, QPushButton, QInputDialog, QMessageBox, QLabel,
    QComboBox, QDateTimeEdit, QLineEdit, QFormLayout, QDialog, QDialogButtonBox,
    QListWidgetItem
)
from PySide6.QtCore import QDateTime, Qt, QSize
import sys
from database import Database
import config_manager

qss_style = '''
QMainWindow { background-color: #f0f0f0; }
QTabWidget::pane { border: 1px solid #cccccc; background: white; }
QTabBar::tab { background: #e0e0e0; border: 1px solid #cccccc; padding: 10px; }
QTabBar::tab:selected { background: #ffffff; font-weight: bold; }
QListWidget, QTextEdit { background: #ffffff; border: 1px solid #cccccc; }
'''

class EditCounselDialog(QDialog):
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
        self.target_combo.addItems(['학생 본인', '보호자', '친구', '기타'])
        self.target_combo.setCurrentText(record['대상'])

        self.method_combo = QComboBox()
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

class PasswordDialogBase(QDialog):
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('암호 입력')
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.form_layout.addRow('암호:', self.password_edit)

    def get_password(self):
        return self.password_edit.text()

class ChangePasswordDialog(PasswordDialogBase):
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

class MainApp(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.setWindowTitle('담임교사용 상담일지')
        self.setGeometry(100, 100, 900, 700)
        self.setFixedSize(QSize(900, 700))
        
        # 데이터베이스 설정
        self.db = db
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.student_tab = QWidget()
        self.tabs.addTab(self.student_tab, '학생 정보')
        self.counsel_tab = QWidget()
        self.tabs.addTab(self.counsel_tab, '상담 기록')
        self.credit_tab = QWidget()
        self.tabs.addTab(self.credit_tab, '프로그램 정보')
        self.init_student_tab()
        self.init_counsel_tab()
        self.init_credit_tab()

    def init_student_tab(self):
        layout = QHBoxLayout()
        self.student_tab.setLayout(layout)
        
        # 왼쪽: 학생 목록 및 버튼
        left_layout = QVBoxLayout()
        self.student_list = QListWidget()
        self.student_list.addItems(self.db.get_all_students())
        left_layout.addWidget(QLabel("학생 목록"))
        left_layout.addWidget(self.student_list)
        
        btn_add = QPushButton('학생 추가')
        btn_del = QPushButton('학생 삭제')
        left_layout.addWidget(btn_add)
        left_layout.addWidget(btn_del)
        layout.addLayout(left_layout, 1)
        
        # 가운데: 학생 정보(연락처/가족) 등 
        center_layout = QVBoxLayout()

        # --- 학생 개별 정보 및 가족 정보 표시 및 수정 폼 ---
        info_group = QWidget()
        info_form = QFormLayout(info_group)
        self.phone_edit = QLineEdit()
        self.gender_edit = QComboBox()
        self.gender_edit.addItems(['남자', '여자', '기타'])
        self.birth_edit = QDateTimeEdit()
        self.birth_edit.setDateTime(QDateTime.currentDateTime())
        self.birth_edit.setDisplayFormat("yyyy-MM-dd")
        self.birth_edit.setCalendarPopup(True)
        self.name_edit = QLineEdit()
        self.format_edit = QComboBox()
        self.format_edit.addItems(['일반(결혼)', '이혼', '재혼', '별거', '동거', '새터민', '다문화', '한부모', '조손', '기타'])
        self.welfare_edit = QComboBox()
        self.welfare_edit.addItems(['일반세대', '국민기초생활수급자', '차상위계층', '저소득층', '장애세대', '독거노인', '국가유공자'])
        self.family_phone_edit1 = QLineEdit()
        self.family_phone_edit2 = QLineEdit()
        self.memo_edit = QTextEdit()
        self.memo_edit.setAcceptRichText(False)
        self.memo_edit.setPlaceholderText("학생에 관한 메모를 입력하세요.")
        btn_save_info = QPushButton("학생 정보 저장")

        info_form.addRow(QLabel("학생 정보"))
        info_form.addRow("이름", self.name_edit)
        info_form.addRow("성별", self.gender_edit)
        info_form.addRow("생년월일", self.birth_edit)
        info_form.addRow("연락처", self.phone_edit)
        info_form.addRow(QLabel(""))
        info_form.addRow(QLabel("가족 정보"))
        info_form.addRow("가정형태", self.format_edit)
        info_form.addRow("보호구분", self.welfare_edit)
        info_form.addRow("보호자 연락처1", self.family_phone_edit1)
        info_form.addRow("보호자 연락처2", self.family_phone_edit2)
        info_form.addRow(QLabel(""))
        info_form.addRow(QLabel("메모"))
        info_form.addRow(self.memo_edit)

        center_layout.addWidget(info_group)
        center_layout.addWidget(btn_save_info)
        layout.addLayout(center_layout, 2)

        # 오른쪽: 상담 기록, 삭제 버튼
        right_layout = QVBoxLayout()

        # --- 상담 기록 표시 및 삭제 ---
        right_layout.addWidget(QLabel("상담 기록"))
        self.counsel_record_list = QListWidget()
        right_layout.addWidget(self.counsel_record_list)
        
        buttons_layout = QHBoxLayout()
        btn_edit_record = QPushButton('상담기록 수정')
        btn_del_record = QPushButton('상담기록 삭제')
        buttons_layout.addWidget(btn_edit_record)
        buttons_layout.addWidget(btn_del_record)

        right_layout.addLayout(buttons_layout)
        layout.addLayout(right_layout, 3)
        
        # 신호 연결
        self.student_list.currentTextChanged.connect(self.display_student_info_and_counsel)
        btn_add.clicked.connect(self.add_student)
        btn_del.clicked.connect(self.delete_student)
        btn_save_info.clicked.connect(self.save_student_info)
        btn_edit_record.clicked.connect(self.edit_counsel_record)
        btn_del_record.clicked.connect(self.delete_counsel_record)

    def display_student_info_and_counsel(self, student_name):
        # UI 초기화
        self.name_edit.clear()
        self.phone_edit.clear()
        self.gender_edit.setCurrentIndex(-1)
        self.birth_edit.setDateTime(QDateTime.currentDateTime())
        self.format_edit.setCurrentIndex(-1)
        self.welfare_edit.setCurrentIndex(-1)
        self.family_phone_edit1.clear()
        self.family_phone_edit2.clear()
        self.memo_edit.clear()
        self.counsel_record_list.clear()
        
        if not student_name:
            return
            
        # 학생 정보 표시
        info = self.db.get_student(student_name)
        if not info:
            return
            
        self.name_edit.setText(student_name)
        if info.get('성별'):
            self.gender_edit.setCurrentText(info['성별'])
        if info.get('생년월일'):
            self.birth_edit.setDateTime(QDateTime.fromString(info['생년월일'], "yyyy-MM-dd"))
        if info.get('연락처'):
            self.phone_edit.setText(info['연락처'])
        if info.get('가정형태'):
            self.format_edit.setCurrentText(info['가정형태'])
        if info.get('보호구분'):
            self.welfare_edit.setCurrentText(info['보호구분'])
        if info.get('보호자 연락처1'):
            self.family_phone_edit1.setText(info['보호자 연락처1'])
        if info.get('보호자 연락처2'):
            self.family_phone_edit2.setText(info['보호자 연락처2'])
        if info.get('메모'):
            self.memo_edit.setText(info['메모'])

        # 상담 기록 표시
        records = self.db.get_counsel_records(student_name)
        if not records:
            self.counsel_record_list.addItem('상담 기록이 없습니다.')
            self.counsel_record_list.setEnabled(False)
            return
            
        self.counsel_record_list.setEnabled(True)
        for rec in records:
            summary = f"[{rec['일시']}] ({rec['대상']}, {rec['방법']}) \n {rec['내용']} \n"
            item = QListWidgetItem(summary)
            item.setData(Qt.UserRole, rec['id'])
            self.counsel_record_list.addItem(item)

    def save_student_info(self):
        current_item = self.student_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "선택 오류", "학생을 선택하세요.")
            return

        original_name = current_item.text()
        updated_name = self.name_edit.text()

        # 학생 이름이 변경된 경우
        if original_name != updated_name:
            if updated_name in self.db.get_all_students():
                QMessageBox.warning(self, "중복 오류", f"'{updated_name}' 학생은 이미 존재합니다.")
                self.name_edit.setText(original_name)  # 원래 이름으로 복원
                return
        
        # 학생 정보 업데이트
        info = {
            '성별': self.gender_edit.currentText(),
            '생년월일': self.birth_edit.dateTime().toString("yyyy-MM-dd"),
            '연락처': self.phone_edit.text(),
            '가정형태': self.format_edit.currentText(),
            '보호구분': self.welfare_edit.currentText(),
            '보호자 연락처1': self.family_phone_edit1.text(),
            '보호자 연락처2': self.family_phone_edit2.text(),
            '메모': self.memo_edit.toPlainText()
        }

        if original_name != updated_name:
            # 이름이 변경된 경우: 기존 학생 삭제 후 새로운 이름으로 추가
            old_records = self.db.get_counsel_records(original_name)
            self.db.delete_student(original_name)
            self.db.add_student(updated_name, info)
            # 상담 기록 복원
            for record in old_records:
                self.db.add_counsel_record(updated_name, record)
            current_item.setText(updated_name)
            self.student_list.sortItems()
        else:
            # 이름이 변경되지 않은 경우: 정보만 업데이트
            self.db.update_student(original_name, info)
        
        self.refresh_student_list()
        QMessageBox.information(self, "저장 완료", "학생 정보가 저장되었습니다.")

    def edit_counsel_record(self):
        student_name = self.student_list.currentItem().text() if self.student_list.currentItem() else None
        if not student_name:
            QMessageBox.warning(self, "선택 오류", "학생을 선택하세요.")
            return
        
        current_item = self.counsel_record_list.currentItem()
        if not current_item or not current_item.data(Qt.UserRole):
            QMessageBox.warning(self, "선택 오류", "수정할 상담기록을 선택하세요.")
            return

        record_id = current_item.data(Qt.UserRole)
        record_to_edit = self.db.get_counsel_record(record_id)
        if not record_to_edit:
            QMessageBox.critical(self, "오류", "상담기록을 불러오지 못했습니다.")
            return

        dialog = EditCounselDialog(record_to_edit, self)
        if dialog.exec():
            updated_data = dialog.get_data()
            if not updated_data['내용']:
                QMessageBox.warning(self, "입력 오류", "상담 내용을 입력하세요.")
                return

            if self.db.update_counsel_record(record_id, updated_data):
                QMessageBox.information(self, "성공", "상담기록이 수정되었습니다.")
                self.display_student_info_and_counsel(student_name)
            else:
                QMessageBox.critical(self, "오류", "상담기록 수정에 실패했습니다.")

    def delete_counsel_record(self):
        student_name = self.student_list.currentItem().text() if self.student_list.currentItem() else None
        if not student_name:
            QMessageBox.warning(self, "선택 오류", "학생을 선택하세요.")
            return
        
        current_item = self.counsel_record_list.currentItem()
        if not current_item or not current_item.data(Qt.UserRole):
            QMessageBox.warning(self, "선택 오류", "삭제할 상담기록을 선택하세요.")
            return
            
        record_id = current_item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self, '상담기록 삭제', "선택한 상담기록을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.db.delete_counsel_record_by_id(record_id):
                self.display_student_info_and_counsel(student_name)

    def add_student(self):
        text, ok = QInputDialog.getText(self, '학생 추가', '학생 이름을 입력하세요:')
        if ok and text:
            if text in self.db.get_all_students():
                QMessageBox.warning(self, "중복", "이미 존재하는 학생입니다.")
                return
            
            if self.db.add_student(text):
                self.student_list.addItem(text)
                self.student_list.sortItems()
                self.refresh_student_list()

    def delete_student(self):
        current_item = self.student_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "선택 오류", "삭제할 학생을 선택하세요.")
            return
            
        name = current_item.text()
        reply = QMessageBox.question(
            self, '학생 삭제', f'{name} 학생을 삭제하시겠습니까?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.db.delete_student(name):
                row = self.student_list.currentRow()
                self.student_list.takeItem(row)
                self.counsel_record_list.clear()
                self.name_edit.clear()
                self.phone_edit.clear()
                self.refresh_student_list()

    def init_counsel_tab(self):
        layout = QVBoxLayout()
        self.counsel_tab.setLayout(layout)
        
        # 상담 학생 선택
        layout.addWidget(QLabel('학생 이름'))
        self.name_combo = QComboBox()
        self.name_combo.setEditable(True)
        self.name_combo.addItems(self.db.get_all_students())
        layout.addWidget(self.name_combo)

        # 상담 대상
        layout.addWidget(QLabel('상담 대상'))
        self.target_combo = QComboBox()
        self.target_combo.addItems(['학생 본인', '보호자', '친구', '기타'])
        layout.addWidget(self.target_combo)
        
        # 상담 일시 선택
        layout.addWidget(QLabel('상담 일시'))
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.datetime_edit.setCalendarPopup(True)
        layout.addWidget(self.datetime_edit)
        
        # 상담 방법 선택
        layout.addWidget(QLabel('상담 방법'))
        self.method_combo = QComboBox()
        self.method_combo.addItems(['대면', '전화', '온라인'])
        layout.addWidget(self.method_combo)
        
        # 상담 내용 입력
        layout.addWidget(QLabel('상담 내용'))
        self.counsel_input = QTextEdit()
        self.counsel_input.setPlaceholderText("상담 내용을 입력하세요.")
        layout.addWidget(self.counsel_input)
        
        # 상담 기록 추가 버튼
        btn_add_counsel = QPushButton('상담 기록 추가')
        layout.addWidget(btn_add_counsel)
        btn_add_counsel.clicked.connect(self.add_counsel_record)

    def add_counsel_record(self):
        name = self.name_combo.currentText()
        if not name:
            QMessageBox.warning(self, "선택 오류", "학생 이름을 입력하거나 선택하세요.")
            return
        if name not in self.db.get_all_students():
            QMessageBox.warning(self, "입력 오류", "학생 이름이 존재하지 않습니다. 정확한 이름을 입력하세요.")
            return
            
        dt = self.datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm")
        target = self.target_combo.currentText()
        method = self.method_combo.currentText()
        content = self.counsel_input.toPlainText().strip()
        
        if not content:
            QMessageBox.warning(self, "입력 오류", "상담 내용을 입력하세요.")
            return
            
        new_record = {'일시': dt, '대상': target, '방법': method, '내용': content}
        if self.db.add_counsel_record(name, new_record):
            # 학생 정보 탭의 상담 기록 갱신
            if self.student_list.currentItem() and self.student_list.currentItem().text() == name:
                self.display_student_info_and_counsel(name)
            self.counsel_input.clear()
            QMessageBox.information(self, "저장 완료", "상담 기록이 추가되었습니다.")

    def refresh_student_list(self):
        # 학생 추가/삭제 후 상담 기록 탭의 콤보박스 갱신
        self.name_combo.clear()
        student_names = [self.student_list.item(i).text() for i in range(self.student_list.count())]
        self.name_combo.addItems(student_names)

    def change_password(self):
        dialog = ChangePasswordDialog(self)
        if dialog.exec():
            old_password, new_password = dialog.get_passwords()

            if not config_manager.check_password(old_password):
                QMessageBox.warning(self, '오류', '기존 암호가 올바르지 않습니다.')
                return

            if config_manager.set_password(new_password):
                QMessageBox.information(self, '성공', '암호가 성공적으로 변경되었습니다.')
            else:
                QMessageBox.critical(self, '오류', '암호 변경에 실패했습니다.')

    def init_credit_tab(self):
        layout = QHBoxLayout()
        self.credit_tab.setLayout(layout)

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel('프로그램명: 담임교사용 상담일지 프로그램\n만든이: 경상북도교육청 전문상담교사 최규호\n라이센스: MIT Lisence'))
        github_label = QLabel('Github: <a href="https://github.com/ghchoi48/HomeRoom-Counseling-Manager">https://github.com/ghchoi48/HomeRoom-Counseling-Manager</a>')
        github_label.setOpenExternalLinks(True)
        left_layout.addWidget(github_label)
        change_password_btn = QPushButton("암호 변경")
        change_password_btn.clicked.connect(self.change_password)
        left_layout.addWidget(QLabel("암호를 잊었을 경우에는 settings.ini 파일을 삭제하세요.\n자료 보존을 위해 counseling.db 파일은 주기적으로 백업하세요."))
        left_layout.addWidget(change_password_btn)
        layout.addLayout(left_layout, 1)
        
        right_layout = QVBoxLayout()
        layout.addLayout(right_layout, 1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qss_style)

    db = None
    if not config_manager.is_password_set():
        dialog = CreatePasswordDialog()
        if dialog.exec():
            password = dialog.get_password()
            config_manager.set_password(password)
        else:
            sys.exit(0)

    while True:
        dialog = PasswordDialog()
        if dialog.exec():
            password = dialog.get_password()
            if config_manager.check_password(password):
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

    if db:
        main_window = MainApp(db)
        main_window.show()
        sys.exit(app.exec())
