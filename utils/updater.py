import requests
from PySide6.QtCore import QObject, Signal

# 현재 애플리케이션 버전
CURRENT_VERSION = "1.3.5"  # 실제 버전에 맞게 수정

class UpdateChecker(QObject):
    # 백그라운드에서 업데이트를 확인하고 완료되면 시그널을 발생시키는 클래스
    
    update_available = Signal(str, str)
    error_occurred = Signal(str)

    def __init__(self, repo_owner, repo_name):
        super().__init__()
        self.repo_owner = repo_owner
        self.repo_name = repo_name

    def check_for_updates(self):
        # GitHub에서 최신 릴리스 버전 정보를 가져와서 필요한 경우 시그널을 발생

        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            release_info = response.json()
            latest_version = release_info["tag_name"].lstrip('v')
            update_content = release_info.get("body", "")
            
            # 버전 비교 (v 접두사 제거 후)
            if latest_version > CURRENT_VERSION:
                self.update_available.emit(latest_version, update_content)
        except requests.RequestException as e:
            error_message = f"Error fetching latest version: {e}"
            print(error_message)
            self.error_occurred.emit(error_message)
