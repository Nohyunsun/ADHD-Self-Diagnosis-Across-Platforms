"""
네이버 블로그 크롤러 설정 파일
"""

# 네이버 API 설정
NAVER_API_CONFIG = {
    'CLIENT_ID': 'YOUR_CLIENT_ID_HERE',  # 네이버 개발자센터에서 발급받은 Client ID
    'CLIENT_SECRET': 'YOUR_CLIENT_SECRET_HERE',  # 네이버 개발자센터에서 발급받은 Client Secret
}

# 크롤링 설정
CRAWLING_CONFIG = {
    'MAX_RESULTS_PER_KEYWORD': 1000,  # 키워드당 최대 수집할 게시글 수
    'REQUEST_DELAY': 0.5,  # API 요청 간 딜레이 (초)
    'PAGE_DELAY': 1.0,  # 페이지 간 딜레이 (초)
    'TIMEOUT': 10,  # HTTP 요청 타임아웃 (초)
    'MAX_COMMENTS_PER_POST': 50,  # 게시글당 최대 수집할 댓글 수
}

# 출력 설정
OUTPUT_CONFIG = {
    'SAVE_CSV': True,  # CSV 파일로 저장 여부
    'SAVE_JSON': True,  # JSON 파일로 저장 여부
    'OUTPUT_DIR': './output/',  # 출력 디렉토리
    'FILENAME_PREFIX': 'naver_blog_',  # 파일명 접두사
}

# 검색 필터 설정
FILTER_CONFIG = {
    'MIN_TITLE_LENGTH': 5,  # 최소 제목 길이
    'MIN_DESCRIPTION_LENGTH': 10,  # 최소 설명 길이
    'EXCLUDE_KEYWORDS': [  # 제외할 키워드 리스트
        '광고', '홍보', '협찬', 'AD'
    ],
}

# 로깅 설정
LOGGING_CONFIG = {
    'LEVEL': 'INFO',  # 로그 레벨 (DEBUG, INFO, WARNING, ERROR)
    'FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'SAVE_TO_FILE': True,  # 파일로 로그 저장 여부
    'LOG_FILE': 'crawler.log',  # 로그 파일명
}