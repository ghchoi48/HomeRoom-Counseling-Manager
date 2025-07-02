import sqlite3
from datetime import datetime
import os
import sys
import csv

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()

class Database:
    def __init__(self, db_file=None):
        if db_file is None:
            db_file = os.path.join(BASE_DIR, 'counseling.db')
        self.db_file = db_file
        self.init_database()

    def get_connection(self):
        """데이터베이스 연결을 가져옵니다."""
        conn = sqlite3.connect(self.db_file)
        return conn

    def check_connection(self):
        """데이터베이스 연결을 테스트합니다."""
        try:
            conn = self.get_connection()
            conn.execute("SELECT count(*) FROM sqlite_master;")
            conn.close()
            return True
        except sqlite3.DatabaseError:
            return False

    def export_to_csv(self, file_path):
        """데이터베이스의 모든 데이터를 CSV 파일로 내보냅니다."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 학생 정보 내보내기
            cursor.execute('''
                SELECT name, phone, gender, birth_date, 
                       guardian_phone1, guardian_phone2, memo,
                       created_at, updated_at
                FROM students
                ORDER BY name
            ''')
            students = cursor.fetchall()
            
            # 상담 기록 내보내기
            cursor.execute('''
                SELECT s.name, cr.counsel_date, cr.target, cr.method, cr.content,
                       cr.created_at
                FROM counseling_records cr
                JOIN students s ON cr.student_id = s.id
                ORDER BY s.name, cr.counsel_date
            ''')
            records = cursor.fetchall()
            
            conn.close()
            
            # CSV 파일 작성
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                
                # 학생 정보 섹션
                writer.writerow(['=== 학생 정보 ==='])
                writer.writerow(['이름', '연락처', '성별', '생년월일', '보호자연락처1', '보호자연락처2', '메모', '생성일시', '수정일시'])
                for student in students:
                    writer.writerow(student)
                
                writer.writerow([])  # 빈 줄
                
                # 상담 기록 섹션
                writer.writerow(['=== 상담 기록 ==='])
                writer.writerow(['학생이름', '상담일시', '상담대상', '상담방법', '상담내용', '생성일시'])
                for record in records:
                    writer.writerow(record)
            
            return True
            
        except Exception as e:
            print(f"CSV 내보내기 오류: {e}")
            return False

    def export_students_to_csv(self, file_path):
        """학생 정보만 CSV 파일로 내보냅니다."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, phone, gender, birth_date, 
                       guardian_phone1, guardian_phone2, memo,
                       created_at, updated_at
                FROM students
                ORDER BY name
            ''')
            students = cursor.fetchall()
            
            conn.close()
            
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['이름', '연락처', '성별', '생년월일', '보호자연락처1', '보호자연락처2', '메모', '생성일시', '수정일시'])
                for student in students:
                    writer.writerow(student)
            
            return True
            
        except Exception as e:
            print(f"학생 정보 CSV 내보내기 오류: {e}")
            return False

    def export_counseling_to_csv(self, file_path):
        """상담 기록만 CSV 파일로 내보냅니다."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.name, cr.counsel_date, cr.target, cr.method, cr.content,
                       cr.created_at
                FROM counseling_records cr
                JOIN students s ON cr.student_id = s.id
                ORDER BY s.name, cr.counsel_date
            ''')
            records = cursor.fetchall()
            
            conn.close()
            
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['학생이름', '상담일시', '상담대상', '상담방법', '상담내용', '생성일시'])
                for record in records:
                    writer.writerow(record)
            
            return True
            
        except Exception as e:
            print(f"상담 기록 CSV 내보내기 오류: {e}")
            return False

    def init_database(self):
        """데이터베이스 및 테이블 초기화"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 학생 정보 테이블
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

        # 상담 기록 테이블
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS counseling_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            counsel_date TIMESTAMP NOT NULL,
            target TEXT NOT NULL,
            method TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
        ''')

        conn.commit()
        conn.close()

    def add_student(self, name, info=None):
        """학생 추가"""
        if info is None:
            info = {}
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO students (
                name, phone, gender, birth_date, 
                guardian_phone1, guardian_phone2, memo
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                name,
                info.get('연락처', ''),
                info.get('성별', ''),
                info.get('생년월일', ''),
                info.get('보호자 연락처1', ''),
                info.get('보호자 연락처2', ''),
                info.get('메모', '')
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def update_student(self, name, info):
        """학생 정보 업데이트"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            UPDATE students SET
                phone = ?,
                gender = ?,
                birth_date = ?,
                guardian_phone1 = ?,
                guardian_phone2 = ?,
                memo = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE name = ?
            ''', (
                info.get('연락처', ''),
                info.get('성별', ''),
                info.get('생년월일', ''),
                info.get('보호자 연락처1', ''),
                info.get('보호자 연락처2', ''),
                info.get('메모', ''),
                name
            ))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete_student(self, name):
        """학생 삭제"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM counseling_records WHERE student_id IN (SELECT id FROM students WHERE name = ?)', (name,))
            cursor.execute('DELETE FROM students WHERE name = ?', (name,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_student(self, name):
        """학생 정보 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT name, phone, gender, birth_date, 
            guardian_phone1, guardian_phone2, memo
        FROM students WHERE name = ?
        ''', (name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                '연락처': row[1],
                '성별': row[2],
                '생년월일': row[3],
                '보호자 연락처1': row[4],
                '보호자 연락처2': row[5],
                '메모': row[6]
            }
        return None

    def get_all_students(self):
        """모든 학생 목록 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT name FROM students ORDER BY name')
        students = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return students

    def add_counsel_record(self, student_name, record):
        """상담 기록 추가"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT id FROM students WHERE name = ?', (student_name,))
            student_id = cursor.fetchone()
            
            if student_id:
                cursor.execute('''
                INSERT INTO counseling_records (
                    student_id, counsel_date, target, method, content
                ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    student_id[0],
                    record['일시'],
                    record['대상'],
                    record['방법'],
                    record['내용']
                ))
                conn.commit()
                return True
            return False
        finally:
            conn.close()

    def get_counsel_records(self, student_name):
        """학생의 상담 기록 조회 (ID 포함)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT cr.id, counsel_date, target, method, content
        FROM counseling_records cr
        JOIN students s ON cr.student_id = s.id
        WHERE s.name = ?
        ORDER BY counsel_date
        ''', (student_name,))
        
        records = []
        for row in cursor.fetchall():
            records.append({
                'id': row[0],
                '일시': row[1],
                '대상': row[2],
                '방법': row[3],
                '내용': row[4]
            })
        
        conn.close()
        return records

    def get_counsel_record(self, record_id):
        """ID로 특정 상담 기록 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, counsel_date, target, method, content
        FROM counseling_records
        WHERE id = ?
        ''', (record_id,))
        
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                '일시': row[1],
                '대상': row[2],
                '방법': row[3],
                '내용': row[4]
            }
        return None

    def update_counsel_record(self, record_id, record_data):
        """상담 기록 업데이트"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
            UPDATE counseling_records SET
                counsel_date = ?,
                target = ?,
                method = ?,
                content = ?
            WHERE id = ?
            ''', (
                record_data['일시'],
                record_data['대상'],
                record_data['방법'],
                record_data['내용'],
                record_id
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"상담 기록 업데이트 오류: {e}")
            return False
        finally:
            conn.close()

    def delete_counsel_record_by_id(self, record_id):
        """ID로 상담 기록 삭제"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM counseling_records WHERE id = ?', (record_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"ID로 상담 기록 삭제 오류: {e}")
            return False
        finally:
            conn.close() 