# YouTube API 크롤러

YouTube Data API v3를 사용하여 키워드 검색 결과의 동영상 정보와 댓글을 크롤링하는 Python 스크립트입니다.

## 기능

- 🔍 키워드로 YouTube 동영상 검색
- 📊 동영상 상세 정보 수집 (조회수, 좋아요 수, 댓글 수 등)
- 💬 동영상 댓글 및 대댓글 수집
- 📅 특정 기간 내 동영상 필터링
- 💾 JSON 및 CSV 형식으로 데이터 저장
- 🔄 배치 크롤링 지원

## 수집 가능한 데이터

### 동영상 정보
- 동영상 ID, 제목, 설명
- 채널명, 채널 ID
- 업로드 날짜
- 조회수, 좋아요 수, 댓글 수
- 동영상 길이, 화질
- 카테고리, 태그
- 썸네일 URL

### 댓글 정보
- 댓글 ID, 작성자명
- 댓글 내용
- 좋아요 수, 작성일시
- 대댓글 여부 및 개수
- 작성자 채널 ID

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. YouTube Data API v3 키 발급
1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. YouTube Data API v3 활성화
4. API 키 생성

### 3. 설정 파일 생성
```bash
cp config_example.py config.py
```

`config.py` 파일을 열어 API 키를 설정하세요:
```python
YOUTUBE_API_KEY = "your_actual_api_key_here"
```

## 사용법

### 1. 대화형 크롤링
```bash
python youtube_crawler.py
```

실행 후 다음 정보를 입력하세요:
- YouTube Data API v3 키
- 검색 키워드
- 최대 동영상 수 (기본값: 50)
- 동영상당 최대 댓글 수 (기본값: 100)
- 검색 기간 (기본값: 최근 30일)
- 저장 형식 (json/csv)

### 2. 배치 크롤링
여러 키워드를 한 번에 크롤링할 수 있습니다.

#### 방법 1: 직접 입력
```bash
python batch_crawler.py
```

#### 방법 2: 파일 사용
`keywords.txt` 파일에 키워드를 한 줄에 하나씩 입력하고:
```
파이썬 프로그래밍
머신러닝 튜토리얼
웹개발 강의
```

```bash
python batch_crawler.py
```

### 3. 프로그래밍 방식 사용
```python
from youtube_crawler import YouTubeCrawler

# 크롤러 초기화
crawler = YouTubeCrawler("your_api_key")

# 키워드 크롤링
result = crawler.crawl_keyword(
    keyword="파이썬 프로그래밍",
    max_videos=50,
    max_comments_per_video=100,
    days_back=30,
    save_format="json"
)

print(f"수집된 동영상: {len(result['videos'])}개")
print(f"수집된 댓글: {len(result['comments'])}개")
```

## 출력 파일

### JSON 형식
```
youtube_data_키워드_20231215_143022.json
```

### CSV 형식
```
youtube_videos_키워드_20231215_143022.csv
youtube_comments_키워드_20231215_143022.csv
```

## API 제한 사항

YouTube Data API v3는 일일 할당량이 있습니다:
- 기본 할당량: 10,000 단위/일
- 검색 요청: 100 단위
- 동영상 정보 요청: 1 단위
- 댓글 요청: 1 단위

할당량 관리를 위해:
- API 호출 간격 조절 (기본 0.1초)
- 적절한 max_results 설정
- 필요한 데이터만 수집

## 주의사항

1. **API 키 보안**: API 키를 공개 저장소에 업로드하지 마세요
2. **저작권**: 수집된 데이터의 사용 시 YouTube 이용약관을 준수하세요
3. **할당량 관리**: API 호출량을 모니터링하고 적절히 조절하세요
4. **에러 처리**: 네트워크 오류나 API 제한 시 재시도 로직을 구현하세요

## 문제 해결

### 403 Forbidden 오류
- API 키가 올바른지 확인
- YouTube Data API v3가 활성화되었는지 확인
- 일일 할당량을 초과했는지 확인

### 댓글 수집 실패
- 댓글이 비활성화된 동영상일 수 있음
- 연령 제한이 있는 동영상일 수 있음

### 느린 크롤링 속도
- API 호출 간격을 줄여보세요 (단, 할당량 주의)
- max_results를 조정하세요
- 병렬 처리를 고려해보세요

## 라이선스

MIT License

## 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.
