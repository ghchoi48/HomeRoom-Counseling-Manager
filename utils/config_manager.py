import configparser
from .helpers import get_base_dir

BASE_DIR = get_base_dir()
CONFIG_FILE = os.path.join(BASE_DIR, 'settings.ini')
PASSWORD_SECTION = 'security'
PASSWORD_OPTION = 'password'

def _hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def is_password_set():
    """설정 파일에 암호가 설정되어 있는지 확인합니다."""
    if not os.path.exists(CONFIG_FILE):
        return False
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')
    return config.has_option(PASSWORD_SECTION, PASSWORD_OPTION)

def check_password(password):
    """입력된 암호가 저장된 해시와 일치하는지 확인합니다."""
    if not is_password_set():
        return False
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')
    stored_hash = config.get(PASSWORD_SECTION, PASSWORD_OPTION)
    return stored_hash == _hash_password(password)

def set_password(password):
    """새 암호를 해시로 변환하여 저장합니다."""
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