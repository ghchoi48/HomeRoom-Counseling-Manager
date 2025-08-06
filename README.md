# HeartWings Lite(마음나래 Lite)

학교에 근무하는 선생님들을 위한 상담 관리 프로그램
학생에 대한 간단한 정보를 등록하여 상담 기록을 관리할 수 있습니다.

## 주요 기능

-   학생 상담 기록 관리
-   NEIS(국가교육정보시스템) 등록용 CSV 파일 내보내기
-   Pyside6 기반 GUI
-   다크 모드 지원
-   UI 폰트 크기 설정

## 사용된 라이브러리

-   Pyside6 (QT)
-   Darkdetect (Alberto Sottile)
-   Requests

## 설치 방법

1. Python 3.13 이상 설치
2. 필요한 패키지 설치:
    ```
    pip install -r requirements.txt
    ```
3. Qt 리소스 파일 생성:
    ```
    pyside6-rcc resources.qrc -o resources_rc.py
    ```

## 실행 방법

```
python main.py
```

## 폴더 구조

-   `main.py` : 메인 진입점
-   `ui/` : UI 관련 코드
-   `utils/` : 설정, 테마 등 유틸리티
-   `resources.qrc` : Qt 리소스 파일

## 라이센스

-   Mit License

## 스크린샷

<img width="902" height="732" alt="스크린샷 2025-07-11 143348" src="https://github.com/user-attachments/assets/f7a24cd3-4b87-4fc7-bb34-80292b4f035c" />

## Trouble Shooting

-   프로그램 실행에 필요한 암호를 잊어버렸다면, settings.ini파일을 삭제하여 암호를 초기화
-   counseling.db 파일을 주기적으로 백업하여 데이터 유실을 방지하기를 권장함

## 문의

프로그램 관련 문의 및 기능 개선 의견은 2023angot_10@sc.gyo6.net로 보내주시거나 [Issues](https://github.com/your-repo/issues)로 남겨주세요.
