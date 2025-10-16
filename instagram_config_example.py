"""
Instagram 크롤러 설정 파일 예시
실제 사용시에는 이 파일을 instagram_config.py로 복사하고 필요한 정보를 입력하세요.
"""

# Instagram 로그인 정보 (선택사항)
# 로그인하면 더 많은 데이터를 수집할 수 있지만, 계정 제재 위험이 있습니다.
INSTAGRAM_USERNAME = "your_instagram_username"
INSTAGRAM_PASSWORD = "your_instagram_password"

# 크롤링 기본 설정
DEFAULT_MAX_POSTS = 50
DEFAULT_MAX_COMMENTS_PER_POST = 100
DEFAULT_DAYS_BACK = 30
DEFAULT_SAVE_FORMAT = "json"  # "json" 또는 "csv"

# 브라우저 설정
HEADLESS_MODE = True  # False로 설정하면 브라우저 창이 보입니다
BROWSER_TIMEOUT = 30  # 브라우저 대기 시간 (초)

# API 호출 간격 (초) - 너무 빠르면 차단될 수 있습니다
REQUEST_DELAY = 2.0
SCROLL_DELAY = 3.0
COMMENT_EXTRACTION_DELAY = 1.0

# 배치 처리 설정
MAX_PARALLEL_WORKERS = 3  # 동시 실행할 최대 크롤러 수
KEYWORD_INTERVAL = 5  # 키워드 간 대기 시간 (초)

# 에러 처리 설정
MAX_RETRIES = 3  # 최대 재시도 횟수
RETRY_DELAY = 10  # 재시도 간격 (초)

# 로그 설정
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "instagram_crawler.log"

# 데이터 저장 경로
OUTPUT_DIRECTORY = "instagram_data"
BACKUP_DIRECTORY = "instagram_data/backup"