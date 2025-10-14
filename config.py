"""
네이버 블로그 크롤러 설정 파일
"""

# 네이버 API 설정
NAVER_API_CONFIG = {
    "CLIENT_ID": "YOUR_CLIENT_ID_HERE",  # 네이버 개발자센터에서 발급받은 클라이언트 ID
    "CLIENT_SECRET": "YOUR_CLIENT_SECRET_HERE"  # 네이버 개발자센터에서 발급받은 클라이언트 시크릿
}

# 크롤링 설정
CRAWLING_CONFIG = {
    "MAX_RESULTS": 100,  # 최대 검색 결과 수
    "REQUEST_DELAY": 1.0,  # 요청 간 딜레이 (초)
    "TIMEOUT": 10,  # 요청 타임아웃 (초)
    "RETRY_COUNT": 3,  # 재시도 횟수
    "INCLUDE_DETAILS": True,  # 상세 정보 포함 여부
}

# 출력 설정
OUTPUT_CONFIG = {
    "SAVE_CSV": True,  # CSV 파일 저장 여부
    "SAVE_JSON": True,  # JSON 파일 저장 여부
    "OUTPUT_DIR": "./output",  # 출력 디렉토리
    "MAX_COMMENT_LENGTH": 200,  # 댓글 최대 길이
    "MAX_COMMENTS_PER_POST": 10,  # 게시글당 최대 댓글 수
}

# 검색 기본 설정
SEARCH_CONFIG = {
    "SORT": "sim",  # 정렬 방식: 'sim'(정확도순), 'date'(날짜순)
    "DISPLAY": 100,  # 한 번에 가져올 검색 결과 수 (최대 100)
}