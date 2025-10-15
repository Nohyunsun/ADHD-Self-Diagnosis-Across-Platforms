"""
설정 파일 예시
실제 사용시에는 이 파일을 config.py로 복사하고 API 키를 입력하세요.
"""

# YouTube Data API v3 키
# Google Cloud Console에서 발급받은 API 키를 입력하세요
# https://console.cloud.google.com/apis/credentials
YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY_HERE"

# 크롤링 기본 설정
DEFAULT_MAX_VIDEOS = 50
DEFAULT_MAX_COMMENTS_PER_VIDEO = 100
DEFAULT_DAYS_BACK = 30
DEFAULT_SAVE_FORMAT = "json"  # "json" 또는 "csv"

# API 호출 간격 (초)
API_CALL_DELAY = 0.1
COMMENT_API_DELAY = 0.5