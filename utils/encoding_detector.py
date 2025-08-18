import charset_normalizer

def detect_encoding(csv_file):
    with open(csv_file, 'rb') as file:
        result = charset_normalizer.from_bytes(file.read()).best()
        if result is None:
            raise ValueError("파일 인코딩을 감지할 수 없습니다.")
        return result.encoding