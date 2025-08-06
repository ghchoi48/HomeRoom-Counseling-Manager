import configparser
import hashlib
import os
from .helpers import get_base_dir

BASE_DIR = get_base_dir()
CONFIG_FILE = os.path.join(BASE_DIR, 'settings.ini')
PASSWORD_SECTION = 'security'
PASSWORD_OPTION = 'password'
DISPLAY_SECTION = 'display'
FONT_SIZE_OPTION = 'fontsize'
SETTINGS_SECTION = 'settings'
SCHOOL_YEAR_OPTION= 'school_year'

CATEGORY = ['학업', '진로', '성격', '성', '대인관계', '가정 및 가족관계', '일탈 및 비행', '학교폭력 가해', '학교폭력 피해', '자해 및 자살', '정신건강', '컴퓨터 및 스마트폰 과사용', '정보제공', '기타']
TARGET = ['학생', '학부모', '교사', '기타']
METHOD = ['면담', '전화상담', '사이버상담']
GENDER = ['남자', '여자', '기타']

def _hash_password(password):
    # 암호를 비문화
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def is_password_set():
    # settings.ini에 암호가 있는지 확인

    if not os.path.exists(CONFIG_FILE):
        return False
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')
    return config.has_option(PASSWORD_SECTION, PASSWORD_OPTION)

def check_password(password):
    # 입력된 암호와 해시가 일치하는지 확인

    if not is_password_set():
        return False
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')
    stored_hash = config.get(PASSWORD_SECTION, PASSWORD_OPTION)
    return stored_hash == _hash_password(password)

def set_password(password):
    # 새 암호를 비문화하여 저장
    
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding='utf-8')

    if not config.has_section(PASSWORD_SECTION):
        config.add_section(PASSWORD_SECTION)
        
    pwd_hash = _hash_password(password)
    config.set(PASSWORD_SECTION, PASSWORD_OPTION, pwd_hash)
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    return True

def get_font_size():
    # 설정 파일에서 글꼴 크기를 가져옴
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding='utf-8')
        if config.has_option(DISPLAY_SECTION, FONT_SIZE_OPTION):
            size_str = config.get(DISPLAY_SECTION, FONT_SIZE_OPTION)
            return size_str.replace('px', '').strip()
    return '13' # 기본값

def set_font_size(size):
    # 글꼴 크기를 설정 파일에 저장
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding='utf-8')

    if not config.has_section(DISPLAY_SECTION):
        config.add_section(DISPLAY_SECTION)
        
    config.set(DISPLAY_SECTION, FONT_SIZE_OPTION, str(size))
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
        config.write(configfile) 