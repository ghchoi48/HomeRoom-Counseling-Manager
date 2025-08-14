# 메인 윈도우 모듈
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QTextEdit, QPushButton, QInputDialog, QMessageBox, QLabel,
    QComboBox, QDateTimeEdit, QLineEdit, QFormLayout, QListWidgetItem,
    QFileDialog, QPlainTextEdit, QDateEdit, QGroupBox
)
import webbrowser
from PySide6.QtCore import QDateTime, Qt, QSize, QThread, Signal

from ui.dialogs import (
    ChangePasswordDialog, EditCounselDialog
)
from utils.config_manager import check_password, set_password, get_font_size, set_font_size, CATEGORY, TARGET, METHOD, GENDER
from utils.updater import CURRENT_VERSION, UpdateChecker
from utils.theme_manager import ThemeManager
from utils.database_worker import DatabaseWorker
from utils.license import LICENSE


class MainApp(QMainWindow):
    update_student_data_signal = Signal(int, dict)
    #메인 애플리케이션 윈도우 클래스
    def __init__(self, theme_manager: ThemeManager):
        super().__init__()
        self.setWindowTitle('마음나래 Lite')
        self.setGeometry(100, 100, 900, 800)
        self.setFixedSize(QSize(900, 800))

        self.theme_manager = theme_manager

        # 데이터베이스 설정 (워커 스레드로 이동)
        self.db_thread = QThread()
        self.db_worker = DatabaseWorker()
        self.db_worker.moveToThread(self.db_thread)

        # DatabaseWorker 시그널 연결
        self.db_worker.students_ready.connect(self.handle_students_ready)
        self.db_worker.student_info_ready.connect(self.handle_student_info_ready)
        self.db_worker.student_data_for_update_ready.connect(self.handle_student_data_for_update)
        self.db_worker.counsel_records_ready.connect(self.handle_counsel_records_ready)
        self.db_worker.counsel_record_ready.connect(self.handle_counsel_record_ready)
        self.db_worker.operation_success.connect(self.handle_db_operation_success)
        self.db_worker.operation_error.connect(self.handle_db_operation_error)
        self.update_student_data_signal.connect(self.db_worker.update_student)
        self.db_worker.import_students_data_ready.connect(self.db_worker.import_students_data)

        #탭 UI 구현
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.student_tab = QWidget()
        self.tabs.addTab(self.student_tab, '학생 정보')
        self.counsel_tab = QWidget()
        self.tabs.addTab(self.counsel_tab, '상담 기록')
        self.credit_tab = QWidget()
        self.tabs.addTab(self.credit_tab, '프로그램 정보 및 설정')
        self.init_student_tab()
        self.init_counsel_tab()
        self.init_credit_tab()

        # 업데이트 확인 스레드 설정
        self.update_thread = QThread()
        self.update_checker = UpdateChecker("ghchoi48", "HomeRoom-Counseling-Manager") # 업데이트 모듈에 Github 아이디, 저장소 이름 전달
        self.update_checker.moveToThread(self.update_thread)
        
        # 시그널 연결
        self.update_thread.started.connect(self.update_checker.check_for_updates)
        self.update_checker.update_available.connect(self.show_update_dialog)
        self.update_checker.error_occurred.connect(self.show_update_error)
        
        # 스레드 시작
        self.update_thread.start()

    def closeEvent(self, event):
        # 어플리케이션 종료 시 업데이트 스레드 정리
        self.update_thread.quit()
        self.update_thread.wait()
        self.db_thread.quit()
        self.db_thread.wait()
        self.db_worker.close_connection()
        super().closeEvent(event)

    def show_update_dialog(self, latest_version, update_content):
        # 업데이트 알림 대화상자 표시 함수
        message = f"새로운 버전({latest_version})이 있습니다.\n\n업데이트 내용:\n{update_content}\n\n업데이트 방법:\ndatabase.db와 settings.ini는 그대로 두고 실행파일만 교체해주세요.\n\n다운로드 페이지로 이동하시겠습니까?"
        reply = QMessageBox.question(
            self,
            "업데이트 가능",
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            webbrowser.open("https://github.com/ghchoi48/HomeRoom-Counseling-Manager/releases")
        self.update_thread.quit()
        self.update_thread.wait()

    def show_update_error(self, error_message):
        # 업데이트 오류 표시 함수
        print(f"Update check failed: {error_message}")
        self.update_thread.quit()
        self.update_thread.wait()

    # --- DatabaseWorker 시그널 핸들러 ---
    def handle_students_ready(self, students):
        self.student_list.clear()
        self.student_list.addItems(students)
        self.name_combo.clear()
        self.name_combo.addItems(students)
        self.db_thread.quit() # 작업 완료 후 스레드 종료
        self.db_thread.wait()

    def handle_student_info_ready(self, info):
        # 학생 정보 표시
        if not info:
            return
        self.name_edit.setText(info.get('이름', ''))
        if info.get('성별'):
            self.gender_edit.setCurrentText(info['성별'])
        if info.get('생년월일'):
            birth_date_str = info.get('생년월일')
            if birth_date_str:
                self.birth_edit.setDateTime(QDateTime.fromString(birth_date_str, "yyyy-MM-dd"))
        if info.get('연락처'):
            self.phone_edit.setText(info['연락처'])
        if info.get('보호자 연락처1'):
            self.family_phone_edit1.setText(info['보호자 연락처1'])
        if info.get('보호자 연락처2'):
            self.family_phone_edit2.setText(info['보호자 연락처2'])
        if info.get('메모'):
            self.memo_edit.setText(info['메모'])

    def handle_student_data_for_update(self, student_data):
        if not student_data:
            QMessageBox.critical(self, "오류", "학생 정보를 데이터베이스에서 찾을 수 없습니다.")
            return
        
        student_id = student_data['id']
        updated_name = self.name_edit.text().strip()

        info = {
            '이름': updated_name,
            '성별': self.gender_edit.currentText(),
            '생년월일': self.birth_edit.dateTime().toString("yyyy-MM-dd"),
            '연락처': self.phone_edit.text(),
            '보호자 연락처1': self.family_phone_edit1.text(),
            '보호자 연락처2': self.family_phone_edit2.text(),
            '메모': self.memo_edit.toPlainText()
        }
        self.update_student_data_signal.emit(student_id, info)
        self.db_thread.start()

    def handle_counsel_records_ready(self, records):
        # 상담 기록 표시
        self.counsel_record_list.clear()
        if not records:
            self.counsel_record_list.addItem('상담 기록이 없습니다.')
            self.counsel_record_list.setEnabled(False)
            return
            
        self.counsel_record_list.setEnabled(True)
        for rec in records:
            summary = f"[{rec['일시']}] ({rec['대상']}, {rec['방법']}, {rec['분류']})\n{rec['내용']}\n"
            item = QListWidgetItem(summary)
            item.setData(Qt.UserRole, rec['id'])
            self.counsel_record_list.addItem(item)
        self.db_thread.quit() # 작업 완료 후 스레드 종료
        self.db_thread.wait()

    def handle_db_operation_success(self, operation_type, data):
        if operation_type == "add_student":
            self.student_list.addItem(data)
            self.student_list.sortItems()
            self.refresh_student_list()
        elif operation_type == "delete_student":
            row = self.student_list.currentRow()
            self.student_list.takeItem(row)
            self.counsel_record_list.clear()
            self.name_edit.clear()
            self.phone_edit.clear()
            self.refresh_student_list()
            QMessageBox.information(self, "삭제 완료", "학생 정보가 성공적으로 삭제되었습니다.")
        elif operation_type == "update_student":
            QMessageBox.information(self, "저장 완료", "학생 정보가 성공적으로 저장되었습니다.")
            # UI의 학생 목록 업데이트
            current_item = self.student_list.currentItem()
            if current_item:
                current_item.setText(data['이름'])
            self.student_list.sortItems()
            # After updating, re-display the current student's info to refresh the form
            if current_item:
                self.display_student_info_and_counsel(current_item.text())
        elif operation_type == "add_counsel_record":
            # 학생 정보 탭의 상담 기록 갱신
            name = self.name_combo.currentText()
            if self.student_list.currentItem() and self.student_list.currentItem().text() == name:
                self.db_worker.get_student_info_and_counsel(name)
                self.db_thread.start()
            self.counsel_input.clear()
            QMessageBox.information(self, "저장 완료", "상담 기록이 추가되었습니다.")
        elif operation_type == "update_counsel_record":
            QMessageBox.information(self, "성공", "상담기록이 수정되었습니다.")
            student_name = self.student_list.currentItem().text() if self.student_list.currentItem() else None
            if student_name:
                self.db_worker.get_student_info_and_counsel(student_name)
                self.db_thread.start()
        elif operation_type == "delete_counsel_record":
            student_name = self.student_list.currentItem().text() if self.student_list.currentItem() else None
            if student_name:
                self.db_worker.get_student_info_and_counsel(student_name)
                self.db_thread.start()
        elif operation_type == "export":
            QMessageBox.information(self, "성공", data)
        elif operation_type == "import":
            QMessageBox.information(self, "성공", data)
            self.refresh_student_list()
        self.db_thread.quit() # 작업 완료 후 스레드 종료
        self.db_thread.wait()

    def handle_db_operation_error(self, error_message):
        QMessageBox.critical(self, "오류", error_message)
        self.db_thread.quit() # 작업 완료 후 스레드 종료
        self.db_thread.wait()

    def init_student_tab(self):
        # 학생 정보탭 초기화 함수

        # 레이아웃 설정
        layout = QHBoxLayout()
        self.student_tab.setLayout(layout)
        
        # 왼쪽: 학생 목록 및 버튼
        left_layout = QVBoxLayout()
        student_list_title = QLabel("학생 목록")
        student_list_title.setProperty("class", "subtitle")
        left_layout.addWidget(student_list_title)
        self.student_list = QListWidget()
        left_layout.addWidget(self.student_list)
        
        
        btn_add = QPushButton('학생 추가')
        btn_del = QPushButton('학생 삭제')
        btn_del.setProperty("class", "danger")
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
        self.gender_edit.addItems(GENDER)
        self.gender_edit.setMinimumWidth(100)
        self.birth_edit = QDateTimeEdit()
        self.birth_edit.setDateTime(QDateTime.currentDateTime())
        self.birth_edit.setDisplayFormat("yyyy-MM-dd")
        self.birth_edit.setCalendarPopup(True)
        self.name_edit = QLineEdit()
        self.family_phone_edit1 = QLineEdit()
        self.family_phone_edit2 = QLineEdit()
        self.memo_edit = QTextEdit()
        self.memo_edit.setMinimumHeight(200)
        self.memo_edit.setAcceptRichText(False)
        self.memo_edit.setPlaceholderText("학생에 관한 메모를 입력하세요.")
        btn_save_info = QPushButton("학생 정보 저장")

        stu_title = QLabel("학생 정보")
        stu_title.setProperty("class", "subtitle")
        info_form.addRow(stu_title)
        info_form.addRow("이름", self.name_edit)
        info_form.addRow("성별", self.gender_edit)
        info_form.addRow("생년월일", self.birth_edit)
        info_form.addRow("연락처", self.phone_edit)
        fam_title = QLabel("가족 정보")
        fam_title.setProperty("class", "subtitle")
        info_form.addRow(fam_title)
        info_form.addRow("보호자 연락처1", self.family_phone_edit1)
        info_form.addRow("보호자 연락처2", self.family_phone_edit2)
        memo_title = QLabel("메모")
        memo_title.setProperty("class", "subtitle")
        info_form.addRow(memo_title)
        info_form.addRow(self.memo_edit)

        center_layout.addWidget(info_group)
        center_layout.addWidget(btn_save_info)
        layout.addLayout(center_layout, 2)

        # 오른쪽: 상담 기록, 삭제 버튼
        right_layout = QVBoxLayout()

        # --- 상담 기록 표시 및 삭제 ---
        counsel_record_title = QLabel("상담 기록")
        counsel_record_title.setProperty("class", "subtitle")
        right_layout.addWidget(counsel_record_title)
        self.counsel_record_list = QListWidget()
        right_layout.addWidget(self.counsel_record_list)
        
        buttons_layout = QHBoxLayout()
        btn_edit_record = QPushButton('상담기록 수정')
        btn_del_record = QPushButton('상담기록 삭제')
        btn_del_record.setProperty("class", "danger")
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
        # 학생 정보 및 상담 내역 표시 함수

        # UI 초기화
        self.name_edit.clear()
        self.phone_edit.clear()
        self.gender_edit.setCurrentIndex(-1)
        self.birth_edit.setDateTime(QDateTime.currentDateTime())
        self.family_phone_edit1.clear()
        self.family_phone_edit2.clear()
        self.memo_edit.clear()
        self.counsel_record_list.clear()
        
        if not student_name:
            return
            
        # 학생 정보 및 상담 기록 조회 요청
        self.db_worker.get_student_info_and_counsel(student_name)
        self.db_thread.start()

    def save_student_info(self):
        # 학생 정보 저장 함수

        current_item = self.student_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "선택 오류", "학생을 선택하세요.")
            return

        original_name = current_item.text()
        updated_name = self.name_edit.text().strip()

        if not updated_name:
            QMessageBox.warning(self, "입력 오류", "학생 이름은 비워둘 수 없습니다.")
            self.name_edit.setText(original_name) # 원래 이름으로 복원
            return

        # 선택된 학생 정보 불러오기
        self.db_worker.get_student_by_name_for_update(original_name)
        self.db_thread.start()

    def edit_counsel_record(self):
        # 상담 기록 수정 함수

        student_name = self.student_list.currentItem().text() if self.student_list.currentItem() else None
        if not student_name:
            QMessageBox.warning(self, "선택 오류", "학생을 선택하세요.")
            return
        
        current_item = self.counsel_record_list.currentItem()
        if not current_item or not current_item.data(Qt.UserRole):
            QMessageBox.warning(self, "선택 오류", "수정할 상담기록을 선택하세요.")
            return

        record_id = current_item.data(Qt.UserRole)
        self.db_worker.get_counsel_record(record_id)
        self.db_thread.start()

    def handle_counsel_record_ready(self, record_to_edit):
        if not record_to_edit:
            QMessageBox.critical(self, "오류", "상담기록을 불러오지 못했습니다.")
            return

        dialog = EditCounselDialog(record_to_edit, self)
        if dialog.exec():
            updated_data = dialog.get_data()
            if not updated_data['내용']:
                QMessageBox.warning(self, "입력 오류", "상담 내용을 입력하세요.")
                return
            self.db_worker.update_counsel_record(record_to_edit['id'], updated_data)
            self.db_thread.start()

    def delete_counsel_record(self):
        # 상담 기록 삭제 함수

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
            self.db_worker.delete_counsel_record_by_id(record_id)
            self.db_thread.start()

    def add_student(self):
        # 학생 추가 함수

        text, ok = QInputDialog.getText(self, '학생 추가', '학생 이름을 입력하세요:')
        if ok and text:
            self.db_worker.add_student(text)
            self.db_thread.start()

    def delete_student(self):
        # 학생 삭제 함수
        
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
            self.db_worker.delete_student(name)
            self.db_thread.start()

    def init_counsel_tab(self):
        # 상담 기록 탭 초기화

        layout = QVBoxLayout()
        self.counsel_tab.setLayout(layout)

        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        row3 = QHBoxLayout()

        # 상담 학생 선택
        row1.addWidget(QLabel('학생 이름'))
        self.name_combo = QComboBox()
        self.name_combo.setMaximumWidth(200)
        self.db_worker.get_all_students()
        self.db_thread.start()
        row1.addWidget(self.name_combo)
        row1.addStretch()

        # 상담 일시 선택
        row2.addWidget(QLabel('상담 일시'))
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.datetime_edit.setMaximumWidth(200)
        self.datetime_edit.setCalendarPopup(True)
        row2.addWidget(self.datetime_edit)
        row2.addStretch()

        # 상담 대상
        row3.addWidget(QLabel('상담 대상'))
        self.target_combo = QComboBox()
        self.target_combo.addItems(TARGET)
        self.target_combo.setMaximumWidth(200)
        row3.addWidget(self.target_combo)
        row3.addSpacing(20)
        # 상담 방법 선택
        row3.addWidget(QLabel('상담 방법'))
        self.method_combo = QComboBox()
        self.method_combo.setMaximumWidth(200)
        self.method_combo.addItems(METHOD)
        row3.addWidget(self.method_combo)
        row3.addSpacing(20)

        # 상담 분류 선택
        row3.addWidget(QLabel('상담 분류'))
        self.category_combo = QComboBox()
        self.category_combo.setMaximumWidth(200)
        self.category_combo.addItems(CATEGORY)
        row3.addWidget(self.category_combo)
        row3.addStretch()

        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addLayout(row3)
        
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
        # 상담 기록 추가 함수

        name = self.name_combo.currentText()
        if not name:
            QMessageBox.warning(self, "선택 오류", "학생 이름을 입력하거나 선택하세요.")
            return
            
        dt = self.datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm")
        target = self.target_combo.currentText()
        method = self.method_combo.currentText()
        category = self.category_combo.currentText()
        content = self.counsel_input.toPlainText().strip()
        
        if not content:
            QMessageBox.warning(self, "입력 오류", "상담 내용을 입력하세요.")
            return
            
        new_record = {'일시': dt, '대상': target, '방법': method, '분류': category, '내용': content}
        self.db_worker.add_counsel_record(name, new_record)
        self.db_thread.start()

    def refresh_student_list(self):
        # 학생 목록 새로고침 함수

        # 학생 추가/삭제 후 상담 기록 탭의 콤보박스 갱신
        self.name_combo.clear()
        self.db_worker.get_all_students()
        self.db_thread.start()

    def change_password(self):
        # 암호 변경 함수

        dialog = ChangePasswordDialog(self)
        if dialog.exec():
            old_password, new_password = dialog.get_passwords()

            if not check_password(old_password):
                QMessageBox.warning(self, '오류', '기존 암호가 올바르지 않습니다.')
                return

            if set_password(new_password):
                QMessageBox.information(self, '성공', '암호가 성공적으로 변경되었습니다.')
            else:
                QMessageBox.critical(self, '오류', '암호 변경에 실패했습니다.')

    def init_credit_tab(self):
        # 프로그램 정보 탭 초기화

        layout = QHBoxLayout()
        self.credit_tab.setLayout(layout)
        
        left_layout = QVBoxLayout()
        program_title = QLabel('마음나래 Lite')
        program_title.setProperty("class", "title")
        left_layout.addWidget(program_title)
        program_discription = QLabel('학교에 근무하는 선생님들을 위한 상담 관리 프로그램')
        program_discription.setProperty("class", "caption")
        left_layout.addWidget(program_discription)
        left_layout.addSpacing(20)
        program_info_title = QLabel('프로그램 정보')
        program_info_title.setProperty("class", "subtitle")
        left_layout.addWidget(program_info_title)
        left_layout.addWidget(QLabel(f'현재 버전: {CURRENT_VERSION}'))
        left_layout.addWidget(QLabel('만든이: 경상북도교육청 전문상담교사 최규호'))
        github_label = QLabel('소스코드: <a href="https://github.com/ghchoi48/HomeRoom-Counseling-Manager">https://github.com/ghchoi48/HomeRoom-Counseling-Manager</a>')
        github_label.setOpenExternalLinks(True)
        github_label.setWordWrap(True)
        left_layout.addWidget(github_label)
        left_layout.addSpacing(20)
        license_label = QLabel('라이센스')
        license_label.setProperty("class", "subtitle")
        license_text = QPlainTextEdit()
        license_text.setReadOnly(True)
        license_text.setPlainText(LICENSE)
        left_layout.addWidget(license_label)
        left_layout.addWidget(license_text)
        
        left_layout.addStretch() # 남은 공간을 채움
        layout.addLayout(left_layout, 1)
        
        right_layout = QVBoxLayout()
        
        # CSV 내보내기 섹션
        data_export_title = QLabel("데이터 내보내기")
        data_export_title.setProperty("class", "subtitle")
        data_export_caption = QLabel("데이터를 CSV 파일로 내보낼 수 있습니다.")
        
        export_btn_row1 = QHBoxLayout()
        export_btn_row2 = QHBoxLayout()
        
        btn_export_all = QPushButton("전체 데이터")
        btn_export_all.clicked.connect(self.export_all_data)
        export_btn_row1.addWidget(btn_export_all)
        
        btn_export_students = QPushButton("학생 정보")
        btn_export_students.clicked.connect(self.export_students_data)
        export_btn_row1.addWidget(btn_export_students)
        
        btn_export_counseling = QPushButton("상담 기록")
        btn_export_counseling.clicked.connect(self.export_counseling_data)
        export_btn_row1.addWidget(btn_export_counseling)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDateTime(QDateTime.currentDateTime())
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDateTime(QDateTime.currentDateTime())
        self.end_date_edit.setCalendarPopup(True)
        
        btn_export_counseling_for_neis = QPushButton("나이스 등록용")
        btn_export_counseling_for_neis.setProperty("class", "success")
        btn_export_counseling_for_neis.clicked.connect(self.export_counseling_data_for_neis)
        
        export_btn_row2.addWidget(self.start_date_edit)
        export_btn_row2.addWidget(QLabel(" ~ "))
        export_btn_row2.addWidget(self.end_date_edit)
        export_btn_row2.addWidget(btn_export_counseling_for_neis)
        export_btn_row2.addStretch()

        # CSV 가져오기 섹션
        import_title = QLabel("데이터 가져오기")
        import_title.setProperty("class", "subtitle")
        import_caption = QLabel("데이터를 CSV 파일로 가져올 수 있습니다.")
        import_btn_row1 = QHBoxLayout()
        import_students_btn = QPushButton("학생 정보 가져오기")
        import_students_btn.clicked.connect(self.import_students_data)
        export_form_students_btn = QPushButton("학생 정보 일괄 등록 양식")
        export_form_students_btn.setProperty("class", "secondary")
        export_form_students_btn.clicked.connect(self.export_form_students_csv)

        import_btn_row1.addWidget(export_form_students_btn)
        import_btn_row1.addWidget(import_students_btn)

        # 글꼴 크기 설정
        
        font_size_label = QLabel("글꼴 크기:")
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems([str(i) for i in range(10, 21)])
        current_font_size = get_font_size()
        self.font_size_combo.setCurrentText(current_font_size)
        self.font_size_combo.currentTextChanged.connect(self.change_font_size)
        font_size_caption = QLabel("기본값은 13 입니다.")
        font_size_caption.setProperty("class", "caption")
        
        font_layout = QHBoxLayout()
        font_layout.addWidget(font_size_label)
        font_layout.addWidget(self.font_size_combo)
        font_layout.addStretch()

        # 암호 변경 버튼
        change_password_title = QLabel("암호 변경")
        change_password_title.setProperty("class", "subtitle")
        change_password_btn = QPushButton("암호 변경")
        change_password_btn.clicked.connect(self.change_password)
        change_password_caption = QLabel("자료 보존을 위해 counseling.db 파일은 주기적으로 백업하세요.")
        change_password_caption.setProperty("class", "caption")
        change_password_caution = QLabel("암호를 잊었을 경우에는 settings.ini 파일을 삭제하세요.")
        change_password_caution.setProperty("class", "caution")
        change_password_hint = QVBoxLayout()
        change_password_hint.addWidget(change_password_caption)
        change_password_hint.addWidget(change_password_caution)
        change_password_hint.setSpacing(0)
        change_password_hint.setContentsMargins(0, 0, 0, 0)

        # 다크모드 토글
        toggle_dark_mode = QPushButton("다크 모드 전환")
        toggle_dark_mode.pressed.connect(self.theme_manager.toggle_theme)

        settings_groupbox = QGroupBox("설정")
        settings_layout = QVBoxLayout()
        settings_layout.addLayout(font_layout)
        settings_layout.addWidget(font_size_caption)
        settings_layout.addWidget(toggle_dark_mode)
        settings_layout.addStretch()
        settings_groupbox.setLayout(settings_layout)

        password_groupbox = QGroupBox("암호")
        password_layout = QVBoxLayout()
        password_layout.addWidget(change_password_btn)
        password_layout.addLayout(change_password_hint)
        password_layout.addStretch()
        password_groupbox.setLayout(password_layout)
    
        export_groupbox = QGroupBox("데이터 내보내기")
        export_layout = QVBoxLayout()
        export_layout.addWidget(data_export_caption)
        export_layout.addLayout(export_btn_row1)
        export_layout.addLayout(export_btn_row2)
        export_layout.addStretch()
        export_groupbox.setLayout(export_layout)

        import_groupbox = QGroupBox("데이터 가져오기")
        import_layout = QVBoxLayout()
        import_layout.addWidget(import_caption)
        import_layout.addLayout(import_btn_row1)
        import_layout.addStretch()
        import_groupbox.setLayout(import_layout)

        right_layout.addWidget(settings_groupbox)
        right_layout.addWidget(password_groupbox)
        right_layout.addWidget(export_groupbox)
        right_layout.addWidget(import_groupbox) 
        right_layout.addStretch()
        layout.addLayout(right_layout, 1)

    def change_font_size(self, size_str):
        size = int(size_str)
        set_font_size(size)
        self.theme_manager.set_font_size(size)

    def import_students_data(self):
        # 학생 정보 CSV 가져오기
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "학생 정보 가져오기", 
            "", 
            "CSV 파일 (*.csv)"
        )
        
        if file_path:
            self.db_worker.import_students_data_ready.emit(file_path)
            self.db_thread.start()

    def export_form_students_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "학생 정보 일괄 등록 양식 저장", 
            "학생정보_일괄등록.csv", 
            "CSV 파일 (*.csv)"
        )

        if file_path:
            self.db_worker.export_form_students_csv(file_path)
            self.db_thread.start()

    def export_all_data(self):
        # 전체 데이터 CSV 내보내기
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "전체 데이터 내보내기", 
            "상담일지_전체데이터.csv", 
            "CSV 파일 (*.csv)"
        )
        
        if file_path:
            self.db_worker.export_all_data(file_path)
            self.db_thread.start()

    def export_students_data(self):
        # 학생 정보 CSV 내보내기
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "학생 정보 내보내기", 
            "상담일지_학생정보.csv", 
            "CSV 파일 (*.csv)"
        )
        
        if file_path:
            self.db_worker.export_students_data(file_path)
            self.db_thread.start()

    def export_counseling_data(self):
        # 상담 기록 CSV 내보내기
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "상담 기록 내보내기", 
            "상담일지_상담기록.csv", 
            "CSV 파일 (*.csv)"
        )
        
        if file_path:
            self.db_worker.export_counseling_data(file_path)
            self.db_thread.start()

    def export_counseling_data_for_neis(self):
        # 나이스 등록용 상담 기록 CSV 내보내기
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "나이스 등록용 상담 기록 내보내기", 
            "나이스_등록용_상담일지_상담기록.csv", 
            "CSV 파일 (*.csv)"
        )
        start_date = self.start_date_edit.dateTime().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.dateTime().toString("yyyy-MM-dd")

        if file_path:
            self.db_worker.export_counseling_data_for_neis(file_path, start_date, end_date)
            self.db_thread.start()