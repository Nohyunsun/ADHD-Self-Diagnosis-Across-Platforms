import requests
import json
import time
from datetime import datetime, timedelta
from urllib.parse import urlencode, urlparse, parse_qs
import csv
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
import re
from bs4 import BeautifulSoup
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class BlogPost:
    """블로그 게시글 정보를 저장하는 데이터 클래스"""
    title: str
    link: str
    description: str
    blog_name: str
    post_date: str
    comments_count: int = 0
    likes_count: int = 0
    comments: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.comments is None:
            self.comments = []

class NaverBlogCrawler:
    """네이버 블로그 크롤링 클래스"""
    
    def __init__(self, client_id: str, client_secret: str):
        """
        네이버 API 클라이언트 초기화
        
        Args:
            client_id: 네이버 개발자센터에서 발급받은 클라이언트 ID
            client_secret: 네이버 개발자센터에서 발급받은 클라이언트 시크릿
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://openapi.naver.com/v1/search/blog.json"
        self.session = requests.Session()
        
        # 요청 헤더 설정
        self.headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def search_blogs(self, query: str, start_date: str = None, end_date: str = None, 
                    display: int = 100, sort: str = 'sim') -> List[Dict[str, Any]]:
        """
        네이버 블로그 검색
        
        Args:
            query: 검색 키워드
            start_date: 검색 시작 날짜 (YYYY-MM-DD 형식)
            end_date: 검색 종료 날짜 (YYYY-MM-DD 형식)
            display: 한 번에 가져올 검색 결과 수 (최대 100)
            sort: 정렬 방식 ('sim': 정확도순, 'date': 날짜순)
            
        Returns:
            검색된 블로그 게시글 리스트
        """
        all_results = []
        start = 1
        max_results = 1000  # 네이버 API 최대 검색 결과 수
        
        while start <= max_results:
            params = {
                'query': query,
                'display': min(display, max_results - start + 1),
                'start': start,
                'sort': sort
            }
            
            try:
                response = self.session.get(self.base_url, headers=self.headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                items = data.get('items', [])
                
                if not items:
                    break
                
                # 날짜 필터링
                filtered_items = self._filter_by_date(items, start_date, end_date)
                all_results.extend(filtered_items)
                
                logger.info(f"검색 결과 {start}-{start + len(items) - 1} 수집 완료")
                
                # 다음 페이지로
                start += display
                
                # API 요청 제한을 위한 딜레이
                time.sleep(0.1)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"API 요청 오류: {e}")
                break
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 오류: {e}")
                break
        
        logger.info(f"총 {len(all_results)}개의 블로그 게시글을 찾았습니다.")
        return all_results
    
    def _filter_by_date(self, items: List[Dict], start_date: str = None, 
                       end_date: str = None) -> List[Dict]:
        """
        날짜 기준으로 검색 결과 필터링
        
        Args:
            items: 검색 결과 아이템 리스트
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
            
        Returns:
            필터링된 아이템 리스트
        """
        if not start_date and not end_date:
            return items
        
        filtered_items = []
        
        for item in items:
            post_date = item.get('postdate', '')
            if post_date:
                try:
                    # postdate는 YYYYMMDD 형식
                    post_datetime = datetime.strptime(post_date, '%Y%m%d')
                    
                    if start_date:
                        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                        if post_datetime < start_datetime:
                            continue
                    
                    if end_date:
                        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                        if post_datetime > end_datetime:
                            continue
                    
                    filtered_items.append(item)
                    
                except ValueError as e:
                    logger.warning(f"날짜 파싱 오류: {post_date}, {e}")
                    # 날짜 파싱에 실패한 경우 포함시킴
                    filtered_items.append(item)
        
        return filtered_items
    
    def get_blog_details(self, blog_url: str) -> Dict[str, Any]:
        """
        개별 블로그 게시글의 상세 정보 크롤링
        
        Args:
            blog_url: 블로그 게시글 URL
            
        Returns:
            댓글 수, 좋아요 수 등 상세 정보
        """
        details = {
            'comments_count': 0,
            'likes_count': 0,
            'comments': []
        }
        
        try:
            # 네이버 블로그 URL 처리
            if 'blog.naver.com' in blog_url:
                details = self._crawl_naver_blog(blog_url)
            else:
                logger.warning(f"지원하지 않는 블로그 플랫폼: {blog_url}")
            
        except Exception as e:
            logger.error(f"블로그 상세 정보 크롤링 오류 ({blog_url}): {e}")
        
        return details
    
    def _crawl_naver_blog(self, blog_url: str) -> Dict[str, Any]:
        """
        네이버 블로그 상세 정보 크롤링
        
        Args:
            blog_url: 네이버 블로그 URL
            
        Returns:
            상세 정보 딕셔너리
        """
        details = {
            'comments_count': 0,
            'likes_count': 0,
            'comments': []
        }
        
        try:
            # 모바일 버전 URL로 변환 (크롤링이 더 쉬움)
            mobile_url = self._convert_to_mobile_url(blog_url)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
            }
            
            response = self.session.get(mobile_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 좋아요 수 추출
            like_elements = soup.find_all(['span', 'div'], class_=re.compile(r'like|sympathy|good', re.I))
            for element in like_elements:
                text = element.get_text(strip=True)
                numbers = re.findall(r'\d+', text)
                if numbers and ('좋아요' in text or '공감' in text or 'like' in text.lower()):
                    details['likes_count'] = int(numbers[0])
                    break
            
            # 댓글 수 추출
            comment_elements = soup.find_all(['span', 'div'], class_=re.compile(r'comment|reply', re.I))
            for element in comment_elements:
                text = element.get_text(strip=True)
                numbers = re.findall(r'\d+', text)
                if numbers and ('댓글' in text or 'comment' in text.lower()):
                    details['comments_count'] = int(numbers[0])
                    break
            
            # 댓글 내용 추출
            details['comments'] = self._extract_comments(soup)
            
        except Exception as e:
            logger.error(f"네이버 블로그 크롤링 오류: {e}")
        
        return details
    
    def _convert_to_mobile_url(self, blog_url: str) -> str:
        """
        데스크톱 블로그 URL을 모바일 URL로 변환
        
        Args:
            blog_url: 원본 블로그 URL
            
        Returns:
            모바일 버전 URL
        """
        try:
            parsed = urlparse(blog_url)
            query_params = parse_qs(parsed.query)
            
            if 'blogId' in query_params and 'logNo' in query_params:
                blog_id = query_params['blogId'][0]
                log_no = query_params['logNo'][0]
                return f"https://m.blog.naver.com/{blog_id}/{log_no}"
        except:
            pass
        
        return blog_url
    
    def _extract_comments(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        댓글 추출
        
        Args:
            soup: BeautifulSoup 객체
            
        Returns:
            댓글 리스트
        """
        comments = []
        
        # 다양한 댓글 선택자 시도
        comment_selectors = [
            '.comment_list .comment_item',
            '.cmt_list .cmt_item',
            '[class*="comment"]',
            '[class*="reply"]'
        ]
        
        for selector in comment_selectors:
            comment_elements = soup.select(selector)
            if comment_elements:
                for element in comment_elements[:10]:  # 최대 10개 댓글만
                    comment_text = element.get_text(strip=True)
                    if comment_text and len(comment_text) > 5:  # 의미있는 댓글만
                        comments.append({
                            'text': comment_text[:200],  # 최대 200자
                            'extracted_at': datetime.now().isoformat()
                        })
                break
        
        return comments
    
    def crawl_blogs(self, query: str, start_date: str = None, end_date: str = None,
                   max_results: int = 100, include_details: bool = True) -> List[BlogPost]:
        """
        블로그 검색 및 상세 정보 크롤링
        
        Args:
            query: 검색 키워드
            start_date: 검색 시작 날짜 (YYYY-MM-DD)
            end_date: 검색 종료 날짜 (YYYY-MM-DD)
            max_results: 최대 결과 수
            include_details: 상세 정보 포함 여부
            
        Returns:
            BlogPost 객체 리스트
        """
        logger.info(f"'{query}' 키워드로 블로그 검색 시작")
        
        # 1단계: 블로그 검색
        search_results = self.search_blogs(query, start_date, end_date)
        
        if max_results:
            search_results = search_results[:max_results]
        
        blog_posts = []
        
        for i, item in enumerate(search_results, 1):
            try:
                # 기본 정보 추출
                blog_post = BlogPost(
                    title=self._clean_html(item.get('title', '')),
                    link=item.get('link', ''),
                    description=self._clean_html(item.get('description', '')),
                    blog_name=self._clean_html(item.get('bloggername', '')),
                    post_date=item.get('postdate', '')
                )
                
                # 상세 정보 크롤링
                if include_details:
                    logger.info(f"상세 정보 크롤링 중... ({i}/{len(search_results)})")
                    details = self.get_blog_details(blog_post.link)
                    blog_post.comments_count = details['comments_count']
                    blog_post.likes_count = details['likes_count']
                    blog_post.comments = details['comments']
                    
                    # 요청 간격 조절
                    time.sleep(1)
                
                blog_posts.append(blog_post)
                
            except Exception as e:
                logger.error(f"블로그 게시글 처리 오류: {e}")
                continue
        
        logger.info(f"총 {len(blog_posts)}개의 블로그 게시글 크롤링 완료")
        return blog_posts
    
    def _clean_html(self, text: str) -> str:
        """HTML 태그 제거 및 텍스트 정리"""
        if not text:
            return ""
        
        # HTML 태그 제거
        clean_text = re.sub(r'<[^>]+>', '', text)
        # HTML 엔티티 디코딩
        clean_text = clean_text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        clean_text = clean_text.replace('&quot;', '"').replace('&#39;', "'")
        
        return clean_text.strip()
    
    def save_to_csv(self, blog_posts: List[BlogPost], filename: str = None):
        """
        크롤링 결과를 CSV 파일로 저장
        
        Args:
            blog_posts: BlogPost 객체 리스트
            filename: 저장할 파일명 (기본값: 현재 시간 기반)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"naver_blog_crawling_{timestamp}.csv"
        
        fieldnames = [
            'title', 'link', 'description', 'blog_name', 'post_date',
            'comments_count', 'likes_count', 'comments_preview'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for post in blog_posts:
                # 댓글 미리보기 (처음 3개 댓글)
                comments_preview = ' | '.join([
                    comment['text'][:50] + '...' if len(comment['text']) > 50 else comment['text']
                    for comment in post.comments[:3]
                ])
                
                writer.writerow({
                    'title': post.title,
                    'link': post.link,
                    'description': post.description,
                    'blog_name': post.blog_name,
                    'post_date': post.post_date,
                    'comments_count': post.comments_count,
                    'likes_count': post.likes_count,
                    'comments_preview': comments_preview
                })
        
        logger.info(f"결과가 {filename}에 저장되었습니다.")
    
    def save_to_json(self, blog_posts: List[BlogPost], filename: str = None):
        """
        크롤링 결과를 JSON 파일로 저장
        
        Args:
            blog_posts: BlogPost 객체 리스트
            filename: 저장할 파일명 (기본값: 현재 시간 기반)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"naver_blog_crawling_{timestamp}.json"
        
        data = [asdict(post) for post in blog_posts]
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=2)
        
        logger.info(f"결과가 {filename}에 저장되었습니다.")


def main():
    """메인 실행 함수"""
    # 네이버 API 키 설정 (실제 사용시 여기에 입력하거나 환경변수 사용)
    CLIENT_ID = "YOUR_CLIENT_ID"
    CLIENT_SECRET = "YOUR_CLIENT_SECRET"
    
    # 크롤러 초기화
    crawler = NaverBlogCrawler(CLIENT_ID, CLIENT_SECRET)
    
    # 검색 설정
    query = "파이썬 프로그래밍"  # 검색할 키워드
    start_date = "2024-01-01"   # 검색 시작 날짜
    end_date = "2024-12-31"     # 검색 종료 날짜
    max_results = 50            # 최대 결과 수
    
    try:
        # 블로그 크롤링 실행
        blog_posts = crawler.crawl_blogs(
            query=query,
            start_date=start_date,
            end_date=end_date,
            max_results=max_results,
            include_details=True
        )
        
        # 결과 저장
        crawler.save_to_csv(blog_posts)
        crawler.save_to_json(blog_posts)
        
        # 결과 요약 출력
        print(f"\n=== 크롤링 결과 요약 ===")
        print(f"총 게시글 수: {len(blog_posts)}")
        print(f"평균 댓글 수: {sum(post.comments_count for post in blog_posts) / len(blog_posts):.1f}")
        print(f"평균 좋아요 수: {sum(post.likes_count for post in blog_posts) / len(blog_posts):.1f}")
        
    except Exception as e:
        logger.error(f"크롤링 실행 오류: {e}")


if __name__ == "__main__":
    main()