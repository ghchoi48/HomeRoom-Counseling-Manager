from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QTextEdit, QPushButton, QInputDialog, QMessageBox, QLabel,
    QComboBox, QDateTimeEdit, QLineEdit, QFormLayout
)
from PySide6.QtCore import QDateTime
import sys

qss_style = '''
QMainWindow { background-color: #f0f0f0; }
QTabWidget::pane { border: 1px solid #cccccc; background: white; }
QTabBar::tab { background: #e0e0e0; border: 1px solid #cccccc; padding: 10px; }
QTabBar::tab:selected { background: #ffffff; font-weight: bold; }
QListWidget, QTextEdit { background: #ffffff; border: 1px solid #cccccc; }
'''

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('담임교사용 상담일지')
        self.setGeometry(100, 100, 900, 600)
        
        # 학생 상담 기록 데이터
        self.records = {
            '학생1': [
                {'일시': '2023-05-10 10:00', '대상': '학생 본인', '방법': '대면', '내용': '학습 동기 부진 상담'},
                {'일시': '2023-06-15 14:30', '대상': '학생 본인', '방법': '전화', '내용': '진로 상담 진행'}
            ],
            '학생2': [
                {'일시': '2023-05-22 09:00', '대상': '학부모', '방법': '대면', '내용': '대인관계 갈등 상담'},
                {'일시': '2023-06-18 13:00', '대상': '학생 본인', '방법': '대면', '내용': '가정 환경 변화 상담'}
            ],
            '학생3': [
                {'일시': '2023-06-01 11:00', '대상': '학생 본인', '방법': '대면', '내용': '진학 상담'},
                {'일시': '2023-06-20 15:00', '대상': '학생 본인', '방법': '대면', '내용': '학습 방법 코칭'}
            ]
        }
        # 학생별 연락처와 가족 정보 저장용 딕셔너리
        self.student_info = {
            '학생1': {'연락처': '010-1111-1111', '성별': '남자', '생년월일': '2008-03-01', '가정형태': '일반(결혼)', '보호구분': '일반세대', '보호자 연락처1': '010-1111-2222', '보호자 연락처2': '', '메모': ''},
            '학생2': {'연락처': '010-2222-2222', '성별': '여자', '생년월일': '2009-03-01', '가정형태': '이혼', '보호구분': '차상위계층', '보호자 연락처1': '010-2222-4444', '보호자 연락처2': '010-2222-3333', '메모': ''},
            '학생3': {'연락처': '010-3333-3333', '성별': '기타', '생년월일': '2010-12-25', '가정형태': '조손', '보호구분': '국가유공자', '보호자 연락처1': '010-3333-4444', '보호자 연락처2': '010-3333-5555', '메모': ''}
        }
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.student_tab = QWidget()
        self.tabs.addTab(self.student_tab, '학생 정보')
        self.counsel_tab = QWidget()
        self.tabs.addTab(self.counsel_tab, '상담 기록')
        self.init_student_tab()
        self.init_counsel_tab()

    def init_student_tab(self):
        layout = QHBoxLayout()
        self.student_tab.setLayout(layout)
        
        # 왼쪽: 학생 목록 및 버튼
        left_layout = QVBoxLayout()
        self.student_list = QListWidget()
        self.student_list.addItems(self.records.keys())
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
        self.sex_edit = QComboBox()
        self.sex_edit.addItems(['남자', '여자', '기타'])
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
        btn_save_info = QPushButton("학생 정보 저장")

        info_form.addRow(QLabel("학생 정보"))
        info_form.addRow("이름", self.name_edit)
        info_form.addRow("성별", self.sex_edit)
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
        btn_del_record = QPushButton('상담기록 삭제')
        right_layout.addWidget(btn_del_record)
        layout.addLayout(right_layout, 3)
        
        # 신호 연결
        self.student_list.currentTextChanged.connect(self.display_student_info_and_counsel)
        btn_add.clicked.connect(self.add_student)
        btn_del.clicked.connect(self.delete_student)
        btn_save_info.clicked.connect(self.save_student_info)
        btn_del_record.clicked.connect(self.delete_counsel_record)

    def display_student_info_and_counsel(self, student_name):
        # 학생 정보 표시
        info = self.student_info.get(student_name, {'연락처': '', '성별': '', '생년월일': '', '가정형태': '', '보호구분': '', '보호자 연락처1': '', '보호자 연락처2': '', '메모': ''})
        self.name_edit.setText(student_name)
        self.sex_edit.setCurrentText(info.get('성별', ''))
        self.birth_edit.setDateTime(QDateTime.fromString(info.get('생년월일', ''), "yyyy-MM-dd"))
        self.phone_edit.setText(info.get('연락처', ''))
        self.format_edit.setCurrentText(info.get('가정형태', ''))
        self.welfare_edit.setCurrentText(info.get('보호구분', ''))
        self.family_phone_edit1.setText(info.get('보호자 연락처1', ''))
        self.family_phone_edit2.setText(info.get('보호자 연락처2', ''))
        self.memo_edit.setText(info.get('메모', ''))

        # 상담 기록 표시
        self.counsel_record_list.clear()
        records = self.records.get(student_name, [])
        if not records:
            self.counsel_record_list.addItem('상담 기록이 없습니다.')
            self.counsel_record_list.setEnabled(False)
            return
        self.counsel_record_list.setEnabled(True)
        for rec in records:
            summary = f"[{rec['일시']}] ({rec['대상']}, {rec['방법']}) \n {rec['내용']} \n"
            self.counsel_record_list.addItem(summary)

    def save_student_info(self):
        student_name = self.student_list.currentItem().text() if self.student_list.currentItem() else None
        if not student_name:
            QMessageBox.warning(self, "선택 오류", "학생을 선택하세요.")
            return
        update_name = self.name_edit.text()
        phone = self.phone_edit.text()
        memo = self.memo_edit.toPlainText()
        self.student_info[student_name] = {'연락처': phone, '메모': memo }
        self.student_info[update_name] = self.student_info.pop(student_name)
        self.records[update_name] = self.records.pop(student_name)
        
        updated_student_list = sorted(self.student_info.items())
        self.student_info = dict(updated_student_list)

        self.student_list.clear()
        self.student_list.addItems(self.student_info.keys())
        self.refresh_student_list()
        QMessageBox.information(self, "저장 완료", "학생 정보가 저장되었습니다.")

    def delete_counsel_record(self):
        student_name = self.student_list.currentItem().text() if self.student_list.currentItem() else None
        if not student_name:
            QMessageBox.warning(self, "선택 오류", "학생을 선택하세요.")
            return
        row = self.counsel_record_list.currentRow()
        records = self.records.get(student_name, [])
        if not records or row < 0 or row >= len(records):
            QMessageBox.warning(self, "선택 오류", "삭제할 상담기록을 선택하세요.")
            return
        reply = QMessageBox.question(
            self, '상담기록 삭제', "선택한 상담기록을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            del self.records[student_name][row]
            self.display_student_info_and_counsel(student_name)

    def add_student(self):
        text, ok = QInputDialog.getText(self, '학생 추가', '학생 이름을 입력하세요:')
        if ok and text:
            if text in self.records:
                QMessageBox.warning(self, "중복", "이미 존재하는 학생입니다.")
                return
            self.records[text] = []
            self.student_info[text] = {'연락처': '', '성별': '', '생년월일': '', '가정형태': '', '보호구분': '', '보호자 연락처1': '', '보호자 연락처2': '', '메모': ''}
            self.student_list.addItem(text)
            sorted_student_list = sorted(self.student_info.items())
            self.student_info = dict(sorted_student_list)
            self.student_list.clear()
            self.student_list.addItems(self.student_info.keys())
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
            row = self.student_list.currentRow()
            self.student_list.takeItem(row)
            if name in self.records:
                del self.records[name]
            if name in self.student_info:
                del self.student_info[name]
            self.counsel_record_list.clear()
            self.phone_edit.clear()
            self.refresh_student_list()

    def init_counsel_tab(self):
        layout = QVBoxLayout()
        self.counsel_tab.setLayout(layout)
        
        # 상담 학생 선택
        layout.addWidget(QLabel('*학생 이름'))
        self.name_combo = QComboBox()
        self.name_combo.setEditable(True)
        self.name_combo.addItems(self.student_info.keys())
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
        layout.addWidget(QLabel('*상담 내용'))
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
        if name not in self.records:
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
        self.records[name].append(new_record)
        # 학생 정보 탭의 상담 기록 갱신
        if self.student_list.currentItem() and self.student_list.currentItem().text() == name:
            self.display_student_info_and_counsel(name)
        self.counsel_input.clear()
        QMessageBox.information(self, "저장 완료", "상담 기록이 추가되었습니다.")

    def refresh_student_list(self):
        # 학생 추가/삭제 후 상담 기록 탭의 콤보박스 갱신
        self.name_combo.clear()
        self.name_combo.addItems(self.student_info.keys())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qss_style)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())
