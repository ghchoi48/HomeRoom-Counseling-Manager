import configparser
import hashlib
import os

CONFIG_FILE = 'config.ini'
PASSWORD_SECTION = 'security'
PASSWORD_OPTION = 'password_hash'
SALT_OPTION = 'salt'

def _get_salt():
    """솔트(salt)를 가져오거나 생성합니다. 솔트는 config 파일에 저장됩니다."""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding='utf-8')
    
    if not config.has_section(PASSWORD_SECTION) or not config.has_option(PASSWORD_SECTION, SALT_OPTION):
        if not config.has_section(PASSWORD_SECTION):
            config.add_section(PASSWORD_SECTION)
        
        salt = os.urandom(16)
        config.set(PASSWORD_SECTION, SALT_OPTION, salt.hex())
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            config.write(f)
        return salt
    
    return bytes.fromhex(config.get(PASSWORD_SECTION, SALT_OPTION))

def _hash_password(password):
    """제공된 비밀번호를 솔트를 사용하여 해시 처리합니다."""
    salt = _get_salt()
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return pwd_hash.hex()

def is_password_set():
    """비밀번호가 설정되어 있는지 확인합니다."""
    if not os.path.exists(CONFIG_FILE):
        return False
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')
    return config.has_option(PASSWORD_SECTION, PASSWORD_OPTION)

def check_password(password):
    """입력된 비밀번호가 저장된 해시와 일치하는지 확인합니다."""
    if not is_password_set():
        return False
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')
    stored_hash = config.get(PASSWORD_SECTION, PASSWORD_OPTION)
    return stored_hash == _hash_password(password)

def set_password(password):
    """새 비밀번호를 설정하고 해시를 저장합니다."""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding='utf-8')

    if not config.has_section(PASSWORD_SECTION):
        config.add_section(PASSWORD_SECTION)
        
    pwd_hash = _hash_password(password)
    config.set(PASSWORD_SECTION, PASSWORD_OPTION, pwd_hash)
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
        config.write(configfile) 