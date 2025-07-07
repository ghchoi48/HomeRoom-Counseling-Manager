## HomeRoom Counseling Manager

-   담임교사용 상담일지 프로그램
-   학교에 있는 누구나 사용할 수 있는 간단한 상담일지 관리 프로그램
-   학생에 대한 간단한 정보와 메모를 작성할 수 있으며, 상담 기록을 작성할 수 있음
-   AntDesign의 디자인 언어를 참고하였음

### License

-   Mit License

### Using Language

-   Python 3.13

### Using Library

-   Pyside6 (QT)
-   Darkdetect (Alberto Sottile)
-   Requests

### Screenshot

![스크린샷 2025-06-25 100146](https://github.com/user-attachments/assets/342dbd12-7dd6-4812-85a7-b4da7ff3394e)

### Fucntions

-   간략한 학생 정보 관리 기능
-   학생 상담 기록 관리 기능
-   데이터 내보내기 기능(CSV)
-   NEIS 등록용 CSV 내보내기 기능
    -   상담 시간은 0시간 10분으로 일괄 지정
    -   내용 수정이 필요한 경우 CSV 파일을 엑셀로 열어 수정하세요

### How to Use

-   프로그램 최초 실행시 암호 설정, 이후 재실행시 설정된 암호 입력하여 실행
-   데이터는 Sqlite3 DB로 보관되며, 실행파일이 위치한 폴더의 counseling.db에 저장됨
-   DB는 암호화되지 않고 접근 제한이 없으므로 보안에 유의하여야 함
-   암호는 비문화(SHA-256) 되어 settings.ini에 저장됨
-   암호 변경은 프로그램 정보탭에서 가능함
-   데이터 가공을 위한 DB데이터 CSV 내보내기 기능(프로그램 정보 탭)

### Trouble Shooting

-   프로그램 실행에 필요한 암호를 잊어버렸다면, settings.ini파일을 삭제하여 암호를 초기화 할 수 있음
-   counseling.db 파일을 주기적으로 백업하여 데이터 유실을 방지하기를 권장함
-   프로그램 관련 문의 및 기능 개선 의견은 2023angot_10@sc.gyo6.net로 보내주세요
