# Tistory Blog Crawler

티스토리 블로그에서 키워드 검색을 통해 게시글, 댓글, 좋아요 수 등을 크롤링하는 Python 도구입니다.

## 🚀 주요 기능

- **키워드 기반 검색**: 티스토리 검색을 통한 관련 게시글 수집
- **기간 필터링**: 지정된 날짜 범위 내의 게시글만 수집
- **상세 정보 수집**: 
  - 게시글 제목, 내용, URL
  - 블로그 이름 및 URL
  - 좋아요(공감) 수
  - 조회수
  - 댓글 수 및 댓글 내용
  - 작성 날짜
- **다양한 출력 형식**: CSV, JSON 파일로 결과 저장
- **두 가지 크롤링 방식**: 
  - 기본 requests/BeautifulSoup 방식
  - Selenium을 이용한 동적 콘텐츠 지원

## 📦 설치 방법

### 1. 저장소 클론
```bash
git clone <repository-url>
cd tistory-crawler
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. Chrome 브라우저 설치 (Selenium 사용 시)
Selenium 버전을 사용하려면 Chrome 브라우저가 설치되어 있어야 합니다.

## 🖥️ 사용 방법

### 기본 크롤러 사용

```python
from tistory_crawler import TistoryCrawler

# 크롤러 인스턴스 생성
crawler = TistoryCrawler(delay=1.0)

# 크롤링 실행
posts = crawler.crawl_keyword_posts(
    keyword="파이썬",
    start_date="2024-01-01",
    end_date="2024-01-31",
    max_pages=5,
    include_details=True
)

# 결과 저장
crawler.save_to_csv(posts, "python_posts.csv")
crawler.save_to_json(posts, "python_posts.json")
```

### Selenium 크롤러 사용

```python
from tistory_selenium_crawler import TistorySeleniumCrawler

# 크롤러 인스턴스 생성
crawler = TistorySeleniumCrawler(headless=True, delay=2.0)

try:
    # 크롤링 실행
    posts = crawler.crawl_keyword_posts(
        keyword="블로그",
        start_date="2024-01-01",
        max_pages=3,
        include_details=True
    )
    
    # 결과 저장
    crawler.save_to_csv(posts)
    
finally:
    # WebDriver 정리
    crawler.driver.quit()
```

### 명령행에서 실행

```bash
# 기본 크롤러
python tistory_crawler.py

# Selenium 크롤러
python tistory_selenium_crawler.py

# 사용 예제
python example_usage.py
```

## 📊 출력 데이터 형식

### CSV 파일 구조
| 컬럼명 | 설명 |
|--------|------|
| title | 게시글 제목 |
| url | 게시글 URL |
| blog_name | 블로그 이름 |
| blog_url | 블로그 URL |
| date | 작성 날짜 |
| content | 게시글 내용 |
| like_count | 좋아요(공감) 수 |
| view_count | 조회수 |
| comment_count | 댓글 수 |
| preview | 미리보기 텍스트 |
| comment_author | 댓글 작성자 |
| comment_content | 댓글 내용 |
| comment_date | 댓글 작성 날짜 |
| crawled_at | 크롤링 시간 |

### JSON 파일 구조
```json
[
  {
    "title": "게시글 제목",
    "url": "https://blog.tistory.com/123",
    "blog_name": "블로그 이름",
    "blog_url": "https://blog.tistory.com",
    "date": "2024.01.15",
    "content": "게시글 전체 내용",
    "like_count": 10,
    "view_count": 150,
    "comment_count": 5,
    "comments": [
      {
        "author": "댓글 작성자",
        "content": "댓글 내용",
        "date": "2024.01.16"
      }
    ],
    "preview": "게시글 미리보기",
    "crawled_at": "2024-01-20T10:30:00"
  }
]
```

## ⚙️ 설정 옵션

### TistoryCrawler 옵션
- `delay`: 요청 간 지연 시간 (초, 기본값: 1.0)

### TistorySeleniumCrawler 옵션
- `headless`: 헤드리스 모드 사용 여부 (기본값: True)
- `delay`: 요청 간 지연 시간 (초, 기본값: 2.0)

### crawl_keyword_posts 매개변수
- `keyword`: 검색할 키워드 (필수)
- `start_date`: 시작 날짜 (YYYY-MM-DD 형식, 선택사항)
- `end_date`: 종료 날짜 (YYYY-MM-DD 형식, 선택사항)
- `max_pages`: 최대 크롤링 페이지 수 (기본값: 10)
- `include_details`: 상세 정보 수집 여부 (기본값: True)

## 🔧 고급 사용법

### 날짜 필터링
```python
from datetime import datetime, timedelta

# 최근 30일간의 게시글만 수집
start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
end_date = datetime.now().strftime('%Y-%m-%d')

posts = crawler.crawl_keyword_posts(
    keyword="검색어",
    start_date=start_date,
    end_date=end_date
)
```

### 커스텀 분석
```python
# 블로그별 게시글 수 분석
blog_counts = {}
for post in posts:
    blog_name = post.get('blog_name', 'Unknown')
    blog_counts[blog_name] = blog_counts.get(blog_name, 0) + 1

# 좋아요 수 상위 게시글
top_liked = sorted(posts, key=lambda x: x.get('like_count', 0), reverse=True)[:10]
```

## ⚠️ 주의사항

1. **속도 제한**: 서버 부하를 방지하기 위해 적절한 지연 시간을 설정하세요.
2. **로봇 배제 표준**: 각 블로그의 robots.txt를 확인하고 준수하세요.
3. **이용 약관**: 티스토리 이용약관을 준수하여 사용하세요.
4. **개인정보**: 수집된 데이터에 개인정보가 포함될 수 있으니 주의하세요.
5. **Chrome 브라우저**: Selenium 버전 사용 시 Chrome 브라우저가 필요합니다.

## 🐛 문제 해결

### Chrome WebDriver 오류
```bash
# Chrome 브라우저 설치 확인
google-chrome --version

# 수동으로 ChromeDriver 설치
pip install webdriver-manager
```

### 인코딩 오류
```python
# CSV 파일을 Excel에서 열 때 한글이 깨지는 경우
df.to_csv("output.csv", index=False, encoding='utf-8-sig')
```

### 메모리 부족
```python
# 대량 데이터 처리 시 배치 처리
def process_in_batches(posts, batch_size=100):
    for i in range(0, len(posts), batch_size):
        batch = posts[i:i+batch_size]
        # 배치 처리 로직
```

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해 주세요.