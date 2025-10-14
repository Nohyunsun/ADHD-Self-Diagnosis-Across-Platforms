# 네이버 블로그 크롤러

네이버 검색 API를 사용하여 블로그 게시글과 댓글, 좋아요 수 등을 크롤링하는 Python 도구입니다.

## 주요 기능

- 🔍 **키워드 기반 블로그 검색**: 네이버 검색 API를 통한 정확한 검색
- 📅 **기간 필터링**: 특정 기간 내의 게시글만 검색 가능
- 💬 **댓글 크롤링**: 각 게시글의 댓글 내용과 개수 수집
- ❤️ **좋아요 수 수집**: 게시글의 공감(좋아요) 수 추출
- 📊 **다양한 출력 형식**: CSV, JSON 형식으로 결과 저장
- ⚡ **효율적인 크롤링**: 요청 제한 및 딜레이 관리

## 설치 방법

1. 저장소 클론 또는 파일 다운로드
2. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## 네이버 API 설정

1. [네이버 개발자센터](https://developers.naver.com/)에서 애플리케이션 등록
2. 검색 API 사용 권한 신청
3. 발급받은 Client ID와 Client Secret을 다음 중 하나의 방법으로 설정:

### 방법 1: config.py 파일 수정
```python
NAVER_API_CONFIG = {
    "CLIENT_ID": "your_actual_client_id",
    "CLIENT_SECRET": "your_actual_client_secret"
}
```

### 방법 2: 환경변수 설정
```bash
export NAVER_CLIENT_ID="your_actual_client_id"
export NAVER_CLIENT_SECRET="your_actual_client_secret"
```

## 사용 방법

### 기본 사용법

```python
from naver_blog_crawler import NaverBlogCrawler

# 크롤러 초기화
crawler = NaverBlogCrawler("YOUR_CLIENT_ID", "YOUR_CLIENT_SECRET")

# 블로그 검색 및 크롤링
blog_posts = crawler.crawl_blogs(
    query="파이썬 프로그래밍",
    max_results=50,
    include_details=True
)

# 결과 저장
crawler.save_to_csv(blog_posts)
crawler.save_to_json(blog_posts)
```

### 날짜 필터링

```python
# 특정 기간의 게시글만 검색
blog_posts = crawler.crawl_blogs(
    query="머신러닝",
    start_date="2024-01-01",
    end_date="2024-12-31",
    max_results=100
)
```

### 상세 옵션

```python
blog_posts = crawler.crawl_blogs(
    query="리액트 개발",           # 검색 키워드
    start_date="2024-01-01",      # 시작 날짜 (YYYY-MM-DD)
    end_date="2024-12-31",        # 종료 날짜 (YYYY-MM-DD)
    max_results=200,              # 최대 결과 수
    include_details=True          # 댓글/좋아요 수 포함 여부
)
```

## 예시 코드 실행

```bash
python example_usage.py
```

예시 코드에서는 다음과 같은 기능을 확인할 수 있습니다:
- 기본 검색
- 날짜 필터링 검색
- 키워드 분석
- 댓글 분석

## 출력 데이터 구조

### CSV 출력 필드
- `title`: 게시글 제목
- `link`: 게시글 URL
- `description`: 게시글 요약
- `blog_name`: 블로그명
- `post_date`: 게시 날짜
- `comments_count`: 댓글 수
- `likes_count`: 좋아요 수
- `comments_preview`: 댓글 미리보기

### JSON 출력 구조
```json
{
  "title": "게시글 제목",
  "link": "게시글 URL",
  "description": "게시글 요약",
  "blog_name": "블로그명",
  "post_date": "20241014",
  "comments_count": 15,
  "likes_count": 32,
  "comments": [
    {
      "text": "댓글 내용",
      "extracted_at": "2024-10-14T10:30:00"
    }
  ]
}
```

## 설정 옵션

`config.py` 파일에서 다양한 설정을 조정할 수 있습니다:

- `MAX_RESULTS`: 최대 검색 결과 수
- `REQUEST_DELAY`: 요청 간 딜레이 (초)
- `TIMEOUT`: 요청 타임아웃 (초)
- `MAX_COMMENT_LENGTH`: 댓글 최대 길이
- `MAX_COMMENTS_PER_POST`: 게시글당 최대 댓글 수

## 주의사항

1. **API 사용 제한**: 네이버 API의 일일 호출 제한을 확인하세요
2. **크롤링 속도**: 과도한 요청을 방지하기 위해 딜레이가 설정되어 있습니다
3. **로봇 배제 표준**: 각 사이트의 robots.txt를 준수하세요
4. **개인정보 보호**: 수집된 데이터의 개인정보를 적절히 처리하세요

## 에러 처리

- 네트워크 오류 시 자동 재시도
- API 제한 초과 시 적절한 오류 메시지
- 잘못된 URL 또는 접근 불가 페이지 건너뛰기
- 상세한 로깅으로 문제 추적 가능

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여하기

버그 리포트나 기능 제안은 GitHub Issues를 통해 제출해 주세요.

---

**면책조항**: 이 도구는 교육 및 연구 목적으로 제작되었습니다. 사용 시 관련 법률과 서비스 약관을 준수해 주세요.