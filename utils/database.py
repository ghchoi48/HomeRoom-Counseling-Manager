import sqlite3
import os
import csv
from contextlib import contextmanager
from utils.helpers import get_base_dir

BASE_DIR = get_base_dir()

class Database:
    def __init__(self, db_file=None):
        if db_file is None:
            db_file = os.path.join(BASE_DIR, 'counseling.db')
        self.db_file = db_file
        self.init_database()

    @contextmanager
    def get_connection(self):
        """데이터베이스 연결 컨텍스트 관리자를 제공합니다."""
        conn = sqlite3.connect(self.db_file)
        try:
            # 외래 키 제약 조건 활성화
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        finally:
            conn.close()

    def check_connection(self):
        """데이터베이스 연결을 테스트합니다."""
        try:
            with self.get_connection() as conn:
                conn.execute("SELECT count(*) FROM sqlite_master;")
            return True
        except sqlite3.DatabaseError:
            return False

    def close_connection(self):
        """데이터베이스 연결을 닫습니다."""
        # 이 클래스는 연결을 유지하지 않으므로 아무것도 하지 않습니다.
        # get_connection()이 컨텍스트 관리자를 사용하여 매번 연결을 열고 닫습니다.
        # 그러나 app.aboutToQuit 시그널에 연결하기 위해 이 메서드를 추가합니다.
        pass

    def _write_csv(self, file_path, headers, data):
        """주어진 데이터를 CSV 파일에 씁니다."""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(data)
            return True
        except IOError as e:
            print(f"CSV 파일 쓰기 오류: {e}")
            return False
        
    def export_counseling_to_csv_for_neis(self, file_path):
        """나이스 등록용 CSV 파일을 내보냅니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT cr.category, REPLACE(date(cr.counsel_date), '-', ''), cr.category, cr.method
                    FROM counseling_records cr
                    JOIN students s ON cr.student_id = s.id
                    ORDER BY cr.counsel_date
                ''')
                records = cursor.fetchall()
                # *상담구분, *상담일자, *상담제목, *상담매체구분

                front_value = ('일반상담', '일반', '상담', '개인상담')
                middle_value1 = ('1', '2025')
                new_records = [ front_value + record[:1] + middle_value1 + record[1:] for record in records] 
                # *상담분류, *Wee클래스, *대분류, *중분류, *상담구분, *상담인원, *학년도, *상담일자, *상담제목, *상담매체구분

                middle_value2 = ('','')
                new_new_records = [ record[:8] + middle_value2 + record[8:] for record in new_records]
                # *상담분류, *Wee클래스, *대분류, *중분류, *상담구분, *상담인원, *학년도, *상담일자, 학년, 성별, *상담제목, *상담매체구분

                middle_value3 = ('일반 상담은 상담 내용을 입력하지 않습니다.', '0', '10', '교사')
                new_new_new_records = [ record[:11] + middle_value3 + record[11:] for record in new_new_records]

            headers = ['*상담분류', '*Wee클래스', '*대분류', '*중분류', '*상담구분', '*상담인원','*학년도','*상담일자','학년','성별','*상담제목','*상담내용','*상담시간(시)','*상담시간(분)','*상담사소속','*상담매체구분']
            return self._write_csv(file_path, headers, new_new_new_records)
        except sqlite3.Error as e:
            print(f"나이스 등록용 CSV 내보내기 오류: {e}")
            return False

    def export_to_csv(self, file_path):
        """데이터베이스의 모든 데이터를 CSV 파일로 내보냅니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT name, phone, gender, birth_date, 
                           guardian_phone1, guardian_phone2, memo,
                           created_at, updated_at
                    FROM students ORDER BY name
                ''')
                students = cursor.fetchall()
                
                cursor.execute('''
                    SELECT s.name, cr.counsel_date, cr.target, cr.method, cr.category, cr.content,
                           cr.created_at
                    FROM counseling_records cr
                    JOIN students s ON cr.student_id = s.id
                    ORDER BY s.name, cr.counsel_date
                ''')
                records = cursor.fetchall()

            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                
                writer.writerow(['=== 학생 정보 ==='])
                writer.writerow(['이름', '연락처', '성별', '생년월일', '보호자연락처1', '보호자연락처2', '메모', '생성일시', '수정일시'])
                writer.writerows(students)
                
                writer.writerow([])
                
                writer.writerow(['=== 상담 기록 ==='])
                writer.writerow(['학생이름', '상담일시', '상담대상', '상담방법', '상담분류', '상담내용', '생성일시'])
                writer.writerows(records)
            
            return True
        except (sqlite3.Error, IOError) as e:
            print(f"CSV 내보내기 오류: {e}")
            return False

    def export_students_to_csv(self, file_path):
        """학생 정보만 CSV 파일로 내보냅니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT name, phone, gender, birth_date, 
                           guardian_phone1, guardian_phone2, memo,
                           created_at, updated_at
                    FROM students ORDER BY name
                ''')
                students = cursor.fetchall()
            
            headers = ['이름', '연락처', '성별', '생년월일', '보호자연락처1', '보호자연락처2', '메모', '생성일시', '수정일시']
            return self._write_csv(file_path, headers, students)
        except sqlite3.Error as e:
            print(f"학생 정보 CSV 내보내기 오류: {e}")
            return False

    def export_counseling_to_csv(self, file_path):
        """상담 기록만 CSV 파일로 내보냅니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT s.name, cr.counsel_date, cr.target, cr.method, cr.category, cr.content, cr.created_at
                    FROM counseling_records cr
                    JOIN students s ON cr.student_id = s.id
                    ORDER BY s.name, cr.counsel_date
                ''')
                records = cursor.fetchall()

            headers = ['학생이름', '상담일시', '상담대상', '상담방법', '상담분류', '상담내용', '생성일시']
            return self._write_csv(file_path, headers, records)
        except sqlite3.Error as e:
            print(f"상담 기록 CSV 내보내기 오류: {e}")
            return False

    def init_database(self):
        try:
            self.create_tables()
            self.update_schema()
        except sqlite3.Error as e:
            print(f"데이터베이스 초기화 오류: {e}")
    
    def create_tables(self):
        """데이터베이스 및 테이블 초기화"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    gender TEXT,
                    birth_date TEXT,
                    guardian_phone1 TEXT,
                    guardian_phone2 TEXT,
                    memo TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS counseling_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    counsel_date TIMESTAMP NOT NULL,
                    target TEXT NOT NULL,
                    method TEXT NOT NULL,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
                )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            print(f"데이터베이스 생성 오류: {e}")

    def update_schema(self):
        """데이터 베이스 스키마 업데이트"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(counseling_records)")
                columns = [info[1] for info in cursor.fetchall()]
                if 'category' not in columns:
                    cursor.execute("ALTER TABLE counseling_records ADD COLUMN category TEXT")
                    conn.commit()
        except sqlite3.Error as e:
            print(f"데이터베이스 스키마 업데이트 오류: {e}")

    def add_student(self, name, info=None):
        """학생 추가"""
        if info is None:
            info = {}
        
        sql = '''
            INSERT INTO students (
                name, phone, gender, birth_date, 
                guardian_phone1, guardian_phone2, memo
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            name,
            info.get('연락처', ''),
            info.get('성별', ''),
            info.get('생년월일', ''),
            info.get('보호자 연락처1', ''),
            info.get('보호자 연락처2', ''),
            info.get('메모', '')
        )
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                conn.commit()
            return True
        except sqlite3.IntegrityError: # 중복된 이름
            return False
        except sqlite3.Error as e:
            print(f"학생 추가 오류: {e}")
            return False

    def update_student(self, student_id, info):
        """학생 정보 업데이트"""
        updated_name = info.get('이름')
        if not updated_name:
            print("학생 이름은 비워둘 수 없습니다.")
            return False

        sql = '''
            UPDATE students SET
                name = ?,
                phone = ?,
                gender = ?,
                birth_date = ?,
                guardian_phone1 = ?,
                guardian_phone2 = ?,
                memo = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        params = (
            updated_name,
            info.get('연락처', ''),
            info.get('성별', ''),
            info.get('생년월일', ''),
            info.get('보호자 연락처1', ''),
            info.get('보호자 연락처2', ''),
            info.get('메모', ''),
            student_id
        )
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            print(f"학생 정보 업데이트 오류: 이름 '{updated_name}'이(가) 이미 존재합니다.")
            return False
        except sqlite3.Error as e:
            print(f"학생 정보 업데이트 오류: {e}")
            return False

    def delete_student(self, name):
        """학생 삭제. ON DELETE CASCADE로 상담기록도 자동 삭제됨."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM students WHERE name = ?', (name,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"학생 삭제 오류: {e}")
            return False

    def get_student(self, name):
        """학생 정보 조회 (id 포함)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, phone, gender, birth_date, 
                           guardian_phone1, guardian_phone2, memo
                    FROM students WHERE name = ?
                ''', (name,))
                row = cursor.fetchone()

            if row:
                return {
                    'id': row[0],
                    '이름': row[1],
                    '연락처': row[2],
                    '성별': row[3],
                    '생년월일': row[4],
                    '보호자 연락처1': row[5],
                    '보호자 연락처2': row[6],
                    '메모': row[7]
                }
            return None
        except sqlite3.Error as e:
            print(f"학생 정보 조회 오류: {e}")
            return None

    def get_student_by_id(self, student_id):
        """ID로 학생 정보 조회"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, phone, gender, birth_date, 
                           guardian_phone1, guardian_phone2, memo
                    FROM students WHERE id = ?
                ''', (student_id,))
                row = cursor.fetchone()

            if row:
                return {
                    'id': row[0],
                    '이름': row[1],
                    '연락처': row[2],
                    '성별': row[3],
                    '생년월일': row[4],
                    '보호자 연락처1': row[5],
                    '보호자 연락처2': row[6],
                    '메모': row[7]
                }
            return None
        except sqlite3.Error as e:
            print(f"학생 정보 조회 오류: {e}")
            return None

    def get_student_by_name(self, name):
        """이름으로 학생 정보 조회 (id 포함)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, phone, gender, birth_date, 
                           guardian_phone1, guardian_phone2, memo
                    FROM students WHERE name = ?
                ''', (name,))
                row = cursor.fetchone()

            if row:
                return {
                    'id': row[0],
                    '이름': row[1],
                    '연락처': row[2],
                    '성별': row[3],
                    '생년월일': row[4],
                    '보호자 연락처1': row[5],
                    '보호자 연락처2': row[6],
                    '메모': row[7]
                }
            return None
        except sqlite3.Error as e:
            print(f"학생 정보 조회 오류: {e}")
            return None

    def get_all_students(self):
        """모든 학생 목록 조회 (이름만)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT name FROM students ORDER BY name')
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"모든 학생 목록 조회 오류: {e}")
            return []

    def add_counsel_record(self, student_name, record):
        """상담 기록 추가"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM students WHERE name = ?', (student_name,))
                student_id_row = cursor.fetchone()
                
                if student_id_row:
                    student_id = student_id_row[0]
                    sql = '''
                        INSERT INTO counseling_records (
                            student_id, counsel_date, target, method, category, content
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    '''
                    params = (
                        student_id,
                        record['일시'],
                        record['대상'],
                        record['방법'],
                        record['분류'],
                        record['내용']
                    )
                    cursor.execute(sql, params)
                    conn.commit()
                    return True
                return False
        except sqlite3.Error as e:
            print(f"상담 기록 추가 오류: {e}")
            return False

    def get_counsel_records(self, student_name):
        """학생의 상담 기록 조회 (ID 포함)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT cr.id, counsel_date, target, method, category, content
                    FROM counseling_records cr
                    JOIN students s ON cr.student_id = s.id
                    WHERE s.name = ?
                    ORDER BY counsel_date DESC
                ''', (student_name,))
                
                return [{
                    'id': row[0], '일시': row[1], '대상': row[2],
                    '방법': row[3], '분류': row[4], '내용': row[5]
                } for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"상담 기록 조회 오류: {e}")
            return []

    def get_counsel_record(self, record_id):
        """ID로 특정 상담 기록 조회"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, counsel_date, target, method, category, content
                    FROM counseling_records WHERE id = ?
                ''', (record_id,))
                row = cursor.fetchone()

            if row:
                return {
                    'id': row[0],
                    '일시': row[1],
                    '대상': row[2],
                    '방법': row[3],
                    '분류': row[4],
                    '내용': row[5]
                }
            return None
        except sqlite3.Error as e:
            print(f"특정 상담 기록 조회 오류: {e}")
            return None

    def update_counsel_record(self, record_id, record_data):
        """상담 기록 업데이트"""
        sql = '''
            UPDATE counseling_records SET
                counsel_date = ?, target = ?, method = ?, category = ?, content = ?
            WHERE id = ?
        '''
        params = (
            record_data['일시'],
            record_data['대상'],
            record_data['방법'],
            record_data['분류'],
            record_data['내용'],
            record_id
        )
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"상담 기록 업데이트 오류: {e}")
            return False

    def delete_counsel_record_by_id(self, record_id):
        """ID로 상담 기록 삭제"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM counseling_records WHERE id = ?', (record_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"ID로 상담 기록 삭제 오류: {e}")
            return False