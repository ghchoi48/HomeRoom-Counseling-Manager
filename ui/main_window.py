# 메인 윈도우 모듈

from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QTextEdit, QPushButton, QInputDialog, QMessageBox, QLabel,
    QComboBox, QDateTimeEdit, QLineEdit, QFormLayout, QListWidgetItem,
    QFileDialog
)
import webbrowser
from PySide6.QtCore import QDateTime, Qt, QSize, QThread

from ui.dialogs import (
    ChangePasswordDialog, EditCounselDialog
)
from utils.config_manager import check_password, set_password
from utils.updater import CURRENT_VERSION, UpdateChecker


class MainApp(QMainWindow):
    #메인 애플리케이션 윈도우 클래스
    def __init__(self, db):
        super().__init__()
        self.setWindowTitle('HomeRoom Counseling Manager')
        self.setGeometry(100, 100, 900, 700)
        self.setFixedSize(QSize(900, 700))
        
        # 데이터베이스 설정
        self.db = db
        
        #탭 UI 구현
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

    def show_update_dialog(self, latest_version, update_content):
        # 업데이트 알림 대화상자 표시 함수
        message = f"새로운 버전({latest_version})이 있습니다.\n\n업데이트 내용:\n{update_content}\n\n다운로드 페이지로 이동하시겠습니까?"
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

    def init_student_tab(self):
        # 학생 정보탭 초기화 함수

        # 레이아웃 설정
        layout = QHBoxLayout()
        self.student_tab.setLayout(layout)
        
        # 왼쪽: 학생 목록 및 버튼
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("학생 목록"))
        self.student_list = QListWidget()
        self.student_list.addItems(self.db.get_all_students())
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
        self.gender_edit.setEditable(True)
        self.gender_edit.addItems(['남자', '여자', '기타'])
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

        info_form.addRow(QLabel("학생 정보"))
        info_form.addRow("이름", self.name_edit)
        info_form.addRow("성별", self.gender_edit)
        info_form.addRow("생년월일", self.birth_edit)
        info_form.addRow("연락처", self.phone_edit)
        info_form.addRow(QLabel(""))
        info_form.addRow(QLabel("가족 정보"))
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
            summary = f"[{rec['일시']}] ({rec['대상']}, {rec['방법']}, {rec['분류']}) \n {rec['내용']} \n"
            item = QListWidgetItem(summary)
            item.setData(Qt.UserRole, rec['id'])
            self.counsel_record_list.addItem(item)

    def save_student_info(self):
        # 학생 정보 저장 함수

        current_item = self.student_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "선택 오류", "학생을 선택하세요.")
            return

        original_name = current_item.text()
        student_data = self.db.get_student(original_name)
        if not student_data:
            QMessageBox.critical(self, "오류", "학생 정보를 데이터베이스에서 찾을 수 없습니다.")
            return
        
        student_id = student_data['id']
        updated_name = self.name_edit.text().strip()

        if not updated_name:
            QMessageBox.warning(self, "입력 오류", "학생 이름은 비워둘 수 없습니다.")
            self.name_edit.setText(original_name) # 원래 이름으로 복원
            return

        # 이름이 변경되었고, 변경된 이름이 이미 다른 학생에게 사용 중인지 확인
        if original_name != updated_name:
            existing_students = self.db.get_all_students()
            if updated_name in existing_students:
                QMessageBox.warning(self, "중복 오류", f"'{updated_name}' 학생은 이미 존재합니다.")
                self.name_edit.setText(original_name)  # 원래 이름으로 복원
                return
        
        # 학생 정보 업데이트
        info = {
            'id': student_id,
            '이름': updated_name,
            '성별': self.gender_edit.currentText(),
            '생년월일': self.birth_edit.dateTime().toString("yyyy-MM-dd"),
            '연락처': self.phone_edit.text(),
            '보호자 연락처1': self.family_phone_edit1.text(),
            '보호자 연락처2': self.family_phone_edit2.text(),
            '메모': self.memo_edit.toPlainText()
        }

        if self.db.update_student(student_id, info):
            QMessageBox.information(self, "저장 완료", "학생 정보가 성공적으로 저장되었습니다.")
            # UI의 학생 목록 업데이트
            current_item.setText(updated_name)
            self.student_list.sortItems()
            self.refresh_student_list()
        else:
            QMessageBox.critical(self, "저장 실패", "학생 정보 저장에 실패했습니다. 이름이 중복되었거나 데이터베이스 오류일 수 있습니다.")
            # 실패 시 UI를 원래대로 되돌릴 수 있도록 원래 이름으로 다시 설정
            self.name_edit.setText(original_name)

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
            if self.db.delete_counsel_record_by_id(record_id):
                self.display_student_info_and_counsel(student_name)

    def add_student(self):
        # 학생 추가 함수

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
            if self.db.delete_student(name):
                row = self.student_list.currentRow()
                self.student_list.takeItem(row)
                self.counsel_record_list.clear()
                self.name_edit.clear()
                self.phone_edit.clear()
                self.refresh_student_list()

    def init_counsel_tab(self):
        # 상담 기록 탭 초기화

        layout = QVBoxLayout()
        self.counsel_tab.setLayout(layout)
        
        # 상담 학생 선택
        layout.addWidget(QLabel('학생 이름'))
        self.name_combo = QComboBox()
        self.name_combo.setEditable(True)
        self.name_combo.setMaximumWidth(200)
        self.name_combo.addItems(self.db.get_all_students())
        layout.addWidget(self.name_combo)

        # 상담 대상
        layout.addWidget(QLabel('상담 대상'))
        self.target_combo = QComboBox()
        self.target_combo.setEditable(True)
        self.target_combo.addItems(['학생 본인', '보호자', '친구', '기타'])
        self.target_combo.setMaximumWidth(200)
        layout.addWidget(self.target_combo)
        
        # 상담 일시 선택
        layout.addWidget(QLabel('상담 일시'))
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.datetime_edit.setMaximumWidth(200)
        self.datetime_edit.setCalendarPopup(True)
        layout.addWidget(self.datetime_edit)
        
        # 상담 방법 선택
        layout.addWidget(QLabel('상담 방법'))
        self.method_combo = QComboBox()
        self.method_combo.setEditable(True)
        self.method_combo.setMaximumWidth(200)
        self.method_combo.addItems(['면담', '전화상담', '사이버상담'])
        layout.addWidget(self.method_combo)

        # 상담 분류 선택
        layout.addWidget(QLabel('상담 분류'))
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.setMaximumWidth(200)
        self.category_combo.addItems(['학업', '진로', '성격', '성', '대인관계', '가정 및 가족관계', '일탈 및 비행', '학교폭력 가해', '학교폭력 피해', '자해 및 자살', '정신건강', '컴퓨터 및 스마트폰 과사용', '정보제공', '기타'])
        layout.addWidget(self.category_combo)
        
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
        if name not in self.db.get_all_students():
            QMessageBox.warning(self, "입력 오류", "학생 이름이 존재하지 않습니다. 정확한 이름을 입력하세요.")
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
        if self.db.add_counsel_record(name, new_record):
            # 학생 정보 탭의 상담 기록 갱신
            if self.student_list.currentItem() and self.student_list.currentItem().text() == name:
                self.display_student_info_and_counsel(name)
            self.counsel_input.clear()
            QMessageBox.information(self, "저장 완료", "상담 기록이 추가되었습니다.")

    def refresh_student_list(self):
        # 학생 목록 새로고침 함수

        # 학생 추가/삭제 후 상담 기록 탭의 콤보박스 갱신
        self.name_combo.clear()
        student_names = [self.student_list.item(i).text() for i in range(self.student_list.count())]
        self.name_combo.addItems(student_names)

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
        left_layout.addWidget(QLabel('담임교사용 상담일지 프로그램'))
        left_layout.addWidget(QLabel(f'현재 버전: {CURRENT_VERSION}'))
        left_layout.addWidget(QLabel('만든이: 경상북도교육청 전문상담교사 최규호'))
        left_layout.addWidget(QLabel('라이센스: MIT Lisence'))
        github_label = QLabel('소스코드: <a href="https://github.com/ghchoi48/HomeRoom-Counseling-Manager">https://github.com/ghchoi48/HomeRoom-Counseling-Manager</a>')
        github_label.setOpenExternalLinks(True)
        left_layout.addWidget(github_label)
        change_password_btn = QPushButton("암호 변경")
        change_password_btn.clicked.connect(self.change_password)
        left_layout.addWidget(QLabel("암호를 잊었을 경우에는 settings.ini 파일을 삭제하세요.\n자료 보존을 위해 counseling.db 파일은 주기적으로 백업하세요."))
        left_layout.addWidget(change_password_btn)
        left_layout.addStretch() # 남은 공간을 채움
        layout.addLayout(left_layout, 1)
        
        right_layout = QVBoxLayout()
        
        # CSV 내보내기 섹션
        right_layout.addWidget(QLabel("데이터 내보내기"))
        right_layout.addWidget(QLabel("데이터를 CSV 파일로 내보낼 수 있습니다."))
        
        btn_export_all = QPushButton("전체 데이터 내보내기")
        btn_export_all.clicked.connect(self.export_all_data)
        right_layout.addWidget(btn_export_all)
        
        btn_export_students = QPushButton("학생 정보만 내보내기")
        btn_export_students.clicked.connect(self.export_students_data)
        right_layout.addWidget(btn_export_students)
        
        btn_export_counseling = QPushButton("상담 기록만 내보내기")
        btn_export_counseling.clicked.connect(self.export_counseling_data)
        right_layout.addWidget(btn_export_counseling)

        btn_export_counseling_for_neis = QPushButton("나이스 등록용 내보내기")
        btn_export_counseling_for_neis.clicked.connect(self.export_counseling_data_for_neis)
        right_layout.addWidget(btn_export_counseling_for_neis)
        
        right_layout.addStretch()  # 남은 공간을 채움
        layout.addLayout(right_layout, 1)

    def export_all_data(self):
        # 전체 데이터 CSV 내보내기
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "전체 데이터 내보내기", 
            "상담일지_전체데이터.csv", 
            "CSV 파일 (*.csv)"
        )
        
        if file_path:
            if self.db.export_to_csv(file_path):
                QMessageBox.information(self, "성공", f"전체 데이터가 성공적으로 내보내졌습니다.\n저장 위치: {file_path}")
            else:
                QMessageBox.critical(self, "오류", "데이터 내보내기에 실패했습니다.")

    def export_students_data(self):
        # 학생 정보 CSV 내보내기
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "학생 정보 내보내기", 
            "상담일지_학생정보.csv", 
            "CSV 파일 (*.csv)"
        )
        
        if file_path:
            if self.db.export_students_to_csv(file_path):
                QMessageBox.information(self, "성공", f"학생 정보가 성공적으로 내보내졌습니다.\n저장 위치: {file_path}")
            else:
                QMessageBox.critical(self, "오류", "학생 정보 내보내기에 실패했습니다.")

    def export_counseling_data(self):
        # 상담 기록 CSV 내보내기
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "상담 기록 내보내기", 
            "상담일지_상담기록.csv", 
            "CSV 파일 (*.csv)"
        )
        
        if file_path:
            if self.db.export_counseling_to_csv(file_path):
                QMessageBox.information(self, "성공", f"상담 기록이 성공적으로 내보내졌습니다.\n저장 위치: {file_path}")
            else:
                QMessageBox.critical(self, "오류", "상담 기록 내보내기에 실패했습니다.")

    def export_counseling_data_for_neis(self):
        # 나이스 등록용 상담 기록 CSV 내보내기
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "나이스 등록용 상담 기록 내보내기", 
            "나이스_등록용_상담일지_상담기록.csv", 
            "CSV 파일 (*.csv)"
        )
        
        if file_path:
            if self.db.export_counseling_to_csv_for_neis(file_path):
                QMessageBox.information(self, "성공", f"나이스 등록용 상담 파일이 성공적으로 내보내졌습니다.\n저장 위치: {file_path}")
            else:
                QMessageBox.critical(self, "오류", "나이스 등록용 상담 파일 내보내기에 실패했습니다.")