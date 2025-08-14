
"""데이터베이스 작업을 위한 워커 클래스"""

from PySide6.QtCore import QObject, Signal, Slot
from .database import Database

class DatabaseWorker(QObject):
    """데이터베이스 작업을 백그라운드에서 처리하는 워커"""
    
    # 작업 완료 후 결과를 메인 스레드로 보내는 시그널
    students_ready = Signal(list)
    student_info_ready = Signal(dict)
    student_data_for_update_ready = Signal(dict)
    counsel_records_ready = Signal(list)
    counsel_record_ready = Signal(dict)
    operation_success = Signal(str, object)  # 작업 종류와 결과 데이터를 전달
    operation_error = Signal(str)
    import_students_data_ready = Signal(str)

    def __init__(self):
        super().__init__()
        self.db = Database()

    @Slot()
    def get_all_students(self):
        """모든 학생 목록을 조회"""
        try:
            students = self.db.get_all_students()
            self.students_ready.emit(students)
        except Exception as e:
            self.operation_error.emit(f"학생 목록 조회 실패: {e}")

    @Slot(str)
    def get_student_info_and_counsel(self, student_name):
        """특정 학생의 정보와 상담 기록을 조회"""
        try:
            info = self.db.get_student(student_name)
            records = self.db.get_counsel_records(student_name)
            self.student_info_ready.emit(info or {})
            self.counsel_records_ready.emit(records or [])
        except Exception as e:
            self.operation_error.emit(f"학생 정보 조회 실패: {e}")

    @Slot(str)
    def add_student(self, name):
        """학생 추가"""
        try:
            if self.db.get_student_by_name(name): # Check if student already exists
                self.operation_error.emit("이미 존재하는 학생입니다.")
                return
            if self.db.add_student(name):
                self.operation_success.emit("add_student", name)
            else:
                self.operation_error.emit("학생 추가에 실패했습니다.")
        except Exception as e:
            self.operation_error.emit(f"학생 추가 실패: {e}")

    @Slot(str)
    def delete_student(self, name):
        """학생 삭제"""
        try:
            if self.db.delete_student(name):
                self.operation_success.emit("delete_student", name)
            else:
                self.operation_error.emit("학생 삭제에 실패했습니다.")
        except Exception as e:
            self.operation_error.emit(f"학생 삭제 실패: {e}")

    @Slot(int, dict)
    def update_student(self, student_id, info):
        """학생 정보 업데이트"""
        try:
            # Check if student exists
            existing_student = self.db.get_student_by_id(student_id)
            if not existing_student:
                self.operation_error.emit("학생 정보를 데이터베이스에서 찾을 수 없습니다.")
                return

            # Check if updated name already exists for another student
            updated_name = info.get('이름')
            if updated_name and updated_name != existing_student.get('이름'):
                existing_same_name = self.db.get_student_by_name(updated_name)
                if existing_same_name and existing_same_name['id'] != student_id:
                    self.operation_error.emit(f"'{updated_name}' 학생은 이미 존재합니다.")
                    return

            update_result = self.db.update_student(student_id, info)
            if update_result:
                self.operation_success.emit("update_student", info)
            else:
                self.operation_error.emit("학생 정보 저장에 실패했습니다.")
        except Exception as e:
            self.operation_error.emit(f"학생 정보 저장 실패: {e}")

    @Slot(str, dict)
    def add_counsel_record(self, name, record):
        """상담 기록 추가"""
        try:
            if not self.db.get_student_by_name(name):
                self.operation_error.emit("학생 이름이 존재하지 않습니다. 정확한 이름을 입력하세요.")
                return
            if self.db.add_counsel_record(name, record):
                self.operation_success.emit("add_counsel_record", record)
            else:
                self.operation_error.emit("상담 기록 추가에 실패했습니다.")
        except Exception as e:
            self.operation_error.emit(f"상담 기록 추가 실패: {e}")

    @Slot(int)
    def get_counsel_record(self, record_id):
        """특정 상담 기록 조회"""
        try:
            record = self.db.get_counsel_record(record_id)
            self.counsel_record_ready.emit(record or {})
        except Exception as e:
            self.operation_error.emit(f"상담 기록 조회 실패: {e}")
            
    @Slot(str)
    def get_student_by_name_for_update(self, student_name):
        """학생 이름으로 학생 정보 조회 (업데이트용)"""
        try:
            student_data = self.db.get_student(student_name)
            self.student_data_for_update_ready.emit(student_data or {})
        except Exception as e:
            self.operation_error.emit(f"학생 정보 조회 실패: {e}")
            
    @Slot(int, dict)
    def update_counsel_record(self, record_id, data):
        """상담 기록 수정"""
        try:
            if self.db.update_counsel_record(record_id, data):
                self.operation_success.emit("update_counsel_record", data)
            else:
                self.operation_error.emit("상담기록 수정에 실패했습니다.")
        except Exception as e:
            self.operation_error.emit(f"상담기록 수정 실패: {e}")

    @Slot(int)
    def delete_counsel_record_by_id(self, record_id):
        """상담 기록 ID로 삭제"""
        try:
            if self.db.delete_counsel_record_by_id(record_id):
                self.operation_success.emit("delete_counsel_record", record_id)
            else:
                self.operation_error.emit("상담기록 삭제에 실패했습니다.")
        except Exception as e:
            self.operation_error.emit(f"상담기록 삭제 실패: {e}")

    @Slot(str)
    def export_all_data(self, file_path):
        if self.db.export_to_csv(file_path):
            self.operation_success.emit("export", f"전체 데이터가 성공적으로 내보내졌습니다.\n저장 위치: {file_path}")
        else:
            self.operation_error.emit("데이터 내보내기에 실패했습니다.")

    @Slot(str)
    def export_students_data(self, file_path):
        if self.db.export_students_to_csv(file_path):
            self.operation_success.emit("export", f"학생 정보가 성공적으로 내보내졌습니다.\n저장 위치: {file_path}")
        else:
            self.operation_error.emit("학생 정보 내보내기에 실패했습니다.")

    @Slot(str)
    def export_counseling_data(self, file_path):
        if self.db.export_counseling_to_csv(file_path):
            self.operation_success.emit("export", f"상담 기록이 성공적으로 내보내졌습니다.\n저장 위치: {file_path}")
        else:
            self.operation_error.emit("상담 기록 내보내기에 실패했습니다.")

    @Slot(str)
    def export_form_students_csv(self, file_path):
        if self.db.export_form_students_csv(file_path):
            self.operation_success.emit("export", f"학생 정보 일괄 등록 양식을 저장했습니다.\n저장 위치: {file_path}")
        else:
            self.operation_error.emit("학생 정보 일괄 등록 양식 저장에 실패했습니다.")

    @Slot(str)
    def export_counseling_data_for_neis(self, file_path, start_date, end_date):
        if self.db.export_counseling_to_csv_for_neis(file_path, start_date, end_date):
            self.operation_success.emit("export", f"나이스 등록용 상담 파일이 성공적으로 내보내졌습니다.\n저장 위치: {file_path}")
        else:
            self.operation_error.emit("나이스 등록용 상담 파일 내보내기에 실패했습니다.")

    @Slot(str)
    def import_students_data(self, file_path):
        if self.db.import_csv_to_students(file_path):
            self.operation_success.emit("import", f"학생 정보를 성공적으로 가져왔습니다.")
        else:
            self.operation_error.emit("학생 정보 가져오기에 실패했습니다.\n동명이인이 있는지 확인하세요.")

    def close_connection(self):
        """워커의 데이터베이스 연결을 닫습니다."""
        self.db.close_connection()
