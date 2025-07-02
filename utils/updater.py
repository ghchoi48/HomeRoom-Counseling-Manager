
import requests
from PySide6.QtWidgets import QMessageBox

# 현재 애플리케이션 버전
CURRENT_VERSION = "1.2.1"  # 실제 버전에 맞게 수정해야 합니다.

def get_latest_version(repo_owner, repo_name):
    """GitHub에서 최신 릴리스 버전 정보를 가져옵니다."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()["tag_name"]
    except requests.RequestException as e:
        print(f"Error fetching latest version: {e}")
        return None

def check_for_updates(parent=None):
    """업데이트를 확인하고 필요한 경우 사용자에게 알립니다."""
    latest_version = get_latest_version("ghchoi48", "HomeRoom-Counseling-Manager")

    if latest_version and latest_version > CURRENT_VERSION:
        reply = QMessageBox.question(
            parent,
            "업데이트 가능",
            f"새로운 버전({latest_version})이 있습니다. 다운로드 페이지로 이동하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            import webbrowser
            webbrowser.open("https://github.com/ghchoi48/HomeRoom-Counseling-Manager/releases")
