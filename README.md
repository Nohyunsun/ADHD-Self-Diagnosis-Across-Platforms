# 네이버 블로그 크롤러

네이버 검색 API를 활용하여 블로그 게시글과 댓글, 공감 수를 크롤링하는 Python 도구입니다.

## 주요 기능

- 🔍 네이버 검색 API를 통한 블로그 게시글 검색
- 📅 날짜 범위 필터링 (특정 기간 내 게시글만 수집)
- 💬 각 게시글의 댓글 수집
- ❤️ 좋아요/공감 수 수집
- 📊 CSV 및 JSON 형태로 결과 저장
- 🔄 대량 데이터 수집을 위한 페이지네이션 지원

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 네이버 개발자센터에서 API 키 발급:
   - [네이버 개발자센터](https://developers.naver.com/main/) 접속
   - 애플리케이션 등록
   - 검색 API 사용 설정
   - Client ID와 Client Secret 발급

3. API 키 설정:
   - `config.py` 파일에서 `CLIENT_ID`와 `CLIENT_SECRET` 값 입력
   - 또는 코드에서 직접 입력

## 사용 방법

### 기본 사용법

```python
from naver_blog_crawler import NaverBlogCrawler

# API 키 설정
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"

# 크롤러 초기화
crawler = NaverBlogCrawler(CLIENT_ID, CLIENT_SECRET)

# 키워드로 검색
results = crawler.crawl_all_results(
    keyword="맛집 추천",
    max_results=100
)

# 결과 저장
crawler.save_to_csv(results)
crawler.save_to_json(results)
```

### 날짜 필터링

```python
# 특정 기간 내 게시글만 수집
results = crawler.crawl_all_results(
    keyword="코로나 백신",
    start_date="2024-01-01",
    end_date="2024-12-31",
    max_results=500
)
```

### 여러 키워드 검색

```python
keywords = ["부동산 투자", "주식 투자", "코인 투자"]
all_results = []

for keyword in keywords:
    results = crawler.crawl_all_results(
        keyword=keyword,
        max_results=50
    )
    all_results.extend(results)

crawler.save_to_csv(all_results, "투자_관련_블로그.csv")
```

## 수집되는 데이터

각 블로그 게시글에 대해 다음 정보를 수집합니다:

- **기본 정보**
  - 제목 (title)
  - 설명/요약 (description)
  - 블로거명 (bloggername)
  - 블로그 링크 (bloggerlink)
  - 게시일 (postdate)
  - 게시글 URL (link)

- **상호작용 데이터**
  - 댓글 목록 (comments)
  - 댓글 수 (comment_count)
  - 좋아요/공감 수 (like_count, sympathy_count)

## 파일 구조

```
├── naver_blog_crawler.py    # 메인 크롤러 클래스
├── example_usage.py         # 사용 예제
├── config.py               # 설정 파일
├── requirements.txt        # 필요한 패키지 목록
└── README.md              # 사용 설명서
```

## 주요 클래스 및 메서드

### NaverBlogCrawler 클래스

#### `__init__(client_id, client_secret)`
- 네이버 API 인증 정보로 크롤러 초기화

#### `search_blogs(keyword, start_date=None, end_date=None, display=100, start=1)`
- 네이버 검색 API로 블로그 게시글 검색
- 날짜 필터링 지원

#### `get_blog_details(blog_url)`
- 개별 블로그 게시글의 상세 정보 크롤링 (댓글, 좋아요 수 등)

#### `crawl_all_results(keyword, start_date=None, end_date=None, max_results=1000)`
- 키워드로 모든 검색 결과 크롤링 (페이지네이션 자동 처리)

#### `save_to_csv(data, filename=None)`
- 크롤링 결과를 CSV 파일로 저장

#### `save_to_json(data, filename=None)`
- 크롤링 결과를 JSON 파일로 저장

## 사용 예제

### 1. 기본 검색
```python
python example_usage.py
# 메뉴에서 1 선택
```

### 2. 날짜 필터링 검색
```python
python example_usage.py
# 메뉴에서 2 선택
```

### 3. 여러 키워드 검색
```python
python example_usage.py
# 메뉴에서 3 선택
```

### 4. 상세 분석
```python
python example_usage.py
# 메뉴에서 4 선택
```

## 주의사항

1. **API 사용 제한**: 네이버 검색 API는 일일 호출 제한이 있습니다. 대량 크롤링 시 주의하세요.

2. **요청 간격**: 서버 부하를 줄이기 위해 요청 간 적절한 딜레이를 설정했습니다.

3. **로봇 배제 표준**: 각 블로그의 robots.txt를 확인하고 준수하세요.

4. **개인정보 보호**: 수집한 데이터의 개인정보 처리에 주의하세요.

5. **저작권**: 크롤링한 콘텐츠의 저작권을 존중하세요.

## 설정 옵션

`config.py` 파일에서 다음 설정을 변경할 수 있습니다:

- API 키 정보
- 크롤링 속도 및 제한
- 출력 형식 및 위치
- 필터링 조건
- 로깅 설정

## 문제 해결

### API 인증 오류
- Client ID와 Client Secret이 올바른지 확인
- 네이버 개발자센터에서 검색 API가 활성화되어 있는지 확인

### 크롤링 실패
- 네트워크 연결 상태 확인
- 대상 블로그의 접근 제한 확인
- User-Agent 및 헤더 설정 확인

### 데이터 누락
- 블로그 플랫폼별로 HTML 구조가 다를 수 있음
- 필요시 CSS 선택자 수정

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여하기

버그 리포트, 기능 요청, 풀 리퀘스트를 환영합니다.

## 연락처

문의사항이 있으시면 이슈를 등록해주세요.