import requests
import json
import time
from datetime import datetime, timedelta
from urllib.parse import quote
from bs4 import BeautifulSoup
import pandas as pd
import re
from typing import List, Dict, Optional


class NaverBlogCrawler:
    """네이버 블로그 크롤러 클래스"""
    
    def __init__(self, client_id: str, client_secret: str):
        """
        네이버 API 인증 정보 초기화
        
        Args:
            client_id (str): 네이버 API 클라이언트 ID
            client_secret (str): 네이버 API 클라이언트 시크릿
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.headers = {
            'X-Naver-Client-Id': client_id,
            'X-Naver-Client-Secret': client_secret,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search_blogs(self, keyword: str, start_date: str = None, end_date: str = None, 
                    display: int = 100, start: int = 1) -> List[Dict]:
        """
        네이버 블로그 검색 API를 사용하여 블로그 게시글 검색
        
        Args:
            keyword (str): 검색 키워드
            start_date (str): 검색 시작 날짜 (YYYY-MM-DD)
            end_date (str): 검색 종료 날짜 (YYYY-MM-DD)
            display (int): 검색 결과 개수 (최대 100)
            start (int): 검색 시작 위치
            
        Returns:
            List[Dict]: 검색된 블로그 게시글 리스트
        """
        url = "https://openapi.naver.com/v1/search/blog"
        
        params = {
            'query': keyword,
            'display': display,
            'start': start,
            'sort': 'date'  # 날짜순 정렬
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            items = data.get('items', [])
            
            # 날짜 필터링
            if start_date or end_date:
                items = self._filter_by_date(items, start_date, end_date)
            
            return items
            
        except requests.exceptions.RequestException as e:
            print(f"API 요청 오류: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            return []
    
    def _filter_by_date(self, items: List[Dict], start_date: str = None, 
                       end_date: str = None) -> List[Dict]:
        """
        날짜 범위로 블로그 게시글 필터링
        
        Args:
            items (List[Dict]): 블로그 게시글 리스트
            start_date (str): 시작 날짜
            end_date (str): 종료 날짜
            
        Returns:
            List[Dict]: 필터링된 게시글 리스트
        """
        filtered_items = []
        
        for item in items:
            post_date = item.get('postdate', '')
            if not post_date:
                continue
                
            try:
                # postdate 형식: YYYYMMDD
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
                
            except ValueError:
                # 날짜 파싱 실패시 해당 아이템 포함
                filtered_items.append(item)
        
        return filtered_items
    
    def get_blog_details(self, blog_url: str) -> Dict:
        """
        개별 블로그 게시글의 상세 정보 크롤링 (댓글, 좋아요 수 등)
        
        Args:
            blog_url (str): 블로그 게시글 URL
            
        Returns:
            Dict: 게시글 상세 정보
        """
        try:
            # 네이버 블로그 URL 처리
            if 'blog.naver.com' in blog_url:
                return self._crawl_naver_blog(blog_url)
            else:
                return self._crawl_general_blog(blog_url)
                
        except Exception as e:
            print(f"블로그 상세 정보 크롤링 오류 ({blog_url}): {e}")
            return {
                'comments': [],
                'comment_count': 0,
                'like_count': 0,
                'sympathy_count': 0
            }
    
    def _crawl_naver_blog(self, blog_url: str) -> Dict:
        """
        네이버 블로그 게시글 상세 크롤링
        
        Args:
            blog_url (str): 네이버 블로그 URL
            
        Returns:
            Dict: 상세 정보
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://blog.naver.com'
            }
            
            response = requests.get(blog_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 댓글 수 추출
            comment_count = self._extract_comment_count(soup)
            
            # 공감 수 추출
            sympathy_count = self._extract_sympathy_count(soup)
            
            # 댓글 내용 추출 (가능한 경우)
            comments = self._extract_comments(soup)
            
            return {
                'comments': comments,
                'comment_count': comment_count,
                'like_count': sympathy_count,  # 네이버는 좋아요 대신 공감
                'sympathy_count': sympathy_count
            }
            
        except Exception as e:
            print(f"네이버 블로그 크롤링 오류: {e}")
            return {
                'comments': [],
                'comment_count': 0,
                'like_count': 0,
                'sympathy_count': 0
            }
    
    def _crawl_general_blog(self, blog_url: str) -> Dict:
        """
        일반 블로그 게시글 크롤링
        
        Args:
            blog_url (str): 블로그 URL
            
        Returns:
            Dict: 상세 정보
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(blog_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 기본적인 정보만 추출 (플랫폼별로 다르므로)
            return {
                'comments': [],
                'comment_count': 0,
                'like_count': 0,
                'sympathy_count': 0
            }
            
        except Exception as e:
            print(f"일반 블로그 크롤링 오류: {e}")
            return {
                'comments': [],
                'comment_count': 0,
                'like_count': 0,
                'sympathy_count': 0
            }
    
    def _extract_comment_count(self, soup: BeautifulSoup) -> int:
        """댓글 수 추출"""
        try:
            # 네이버 블로그 댓글 수 선택자들
            selectors = [
                '.blog_comment_count',
                '.comment_count',
                '[class*="comment"]',
                '[id*="comment"]'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text()
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        return int(numbers[0])
            
            return 0
        except:
            return 0
    
    def _extract_sympathy_count(self, soup: BeautifulSoup) -> int:
        """공감 수 추출"""
        try:
            # 네이버 블로그 공감 수 선택자들
            selectors = [
                '.blog_sympathy_count',
                '.sympathy_count',
                '[class*="sympathy"]',
                '[class*="like"]',
                '[id*="sympathy"]'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text()
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        return int(numbers[0])
            
            return 0
        except:
            return 0
    
    def _extract_comments(self, soup: BeautifulSoup) -> List[Dict]:
        """댓글 내용 추출"""
        try:
            comments = []
            
            # 네이버 블로그 댓글 선택자들
            comment_selectors = [
                '.comment_item',
                '.comment_list li',
                '[class*="comment"]'
            ]
            
            for selector in comment_selectors:
                comment_elements = soup.select(selector)
                if comment_elements:
                    for element in comment_elements:
                        comment_text = element.get_text().strip()
                        if comment_text and len(comment_text) > 10:  # 의미있는 댓글만
                            comments.append({
                                'text': comment_text,
                                'author': 'Unknown'  # 작성자 정보는 추가 파싱 필요
                            })
                    break
            
            return comments[:50]  # 최대 50개 댓글만
        except:
            return []
    
    def crawl_all_results(self, keyword: str, start_date: str = None, 
                         end_date: str = None, max_results: int = 1000) -> List[Dict]:
        """
        키워드로 모든 블로그 검색 결과 크롤링
        
        Args:
            keyword (str): 검색 키워드
            start_date (str): 시작 날짜 (YYYY-MM-DD)
            end_date (str): 종료 날짜 (YYYY-MM-DD)
            max_results (int): 최대 결과 수
            
        Returns:
            List[Dict]: 크롤링된 모든 블로그 데이터
        """
        all_results = []
        start = 1
        display = 100
        
        print(f"키워드 '{keyword}' 검색 시작...")
        
        while len(all_results) < max_results:
            print(f"페이지 {start//display + 1} 검색 중... (현재 {len(all_results)}개 수집)")
            
            # 블로그 검색
            items = self.search_blogs(keyword, start_date, end_date, display, start)
            
            if not items:
                print("더 이상 검색 결과가 없습니다.")
                break
            
            # 각 게시글의 상세 정보 크롤링
            for i, item in enumerate(items):
                if len(all_results) >= max_results:
                    break
                
                print(f"  게시글 {i+1}/{len(items)} 처리 중...")
                
                # 기본 정보
                blog_data = {
                    'title': item.get('title', '').replace('<b>', '').replace('</b>', ''),
                    'description': item.get('description', '').replace('<b>', '').replace('</b>', ''),
                    'bloggername': item.get('bloggername', ''),
                    'bloggerlink': item.get('bloggerlink', ''),
                    'postdate': item.get('postdate', ''),
                    'link': item.get('link', '')
                }
                
                # 상세 정보 크롤링
                details = self.get_blog_details(item.get('link', ''))
                blog_data.update(details)
                
                all_results.append(blog_data)
                
                # API 호출 제한을 위한 딜레이
                time.sleep(0.5)
            
            start += display
            
            # API 호출 제한을 위한 딜레이
            time.sleep(1)
        
        print(f"총 {len(all_results)}개의 블로그 게시글을 수집했습니다.")
        return all_results
    
    def save_to_csv(self, data: List[Dict], filename: str = None):
        """
        크롤링 결과를 CSV 파일로 저장
        
        Args:
            data (List[Dict]): 크롤링 데이터
            filename (str): 저장할 파일명
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'naver_blog_crawling_{timestamp}.csv'
        
        # 댓글 데이터를 문자열로 변환
        processed_data = []
        for item in data:
            processed_item = item.copy()
            if 'comments' in processed_item:
                comments_text = []
                for comment in processed_item['comments']:
                    if isinstance(comment, dict):
                        comments_text.append(comment.get('text', ''))
                    else:
                        comments_text.append(str(comment))
                processed_item['comments'] = ' | '.join(comments_text)
            processed_data.append(processed_item)
        
        df = pd.DataFrame(processed_data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"결과가 '{filename}' 파일에 저장되었습니다.")
    
    def save_to_json(self, data: List[Dict], filename: str = None):
        """
        크롤링 결과를 JSON 파일로 저장
        
        Args:
            data (List[Dict]): 크롤링 데이터
            filename (str): 저장할 파일명
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'naver_blog_crawling_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"결과가 '{filename}' 파일에 저장되었습니다.")


def main():
    """메인 실행 함수"""
    # API 키 설정 (실제 사용시 여기에 입력)
    CLIENT_ID = "YOUR_CLIENT_ID"
    CLIENT_SECRET = "YOUR_CLIENT_SECRET"
    
    # 크롤러 초기화
    crawler = NaverBlogCrawler(CLIENT_ID, CLIENT_SECRET)
    
    # 검색 설정
    keyword = "파이썬"  # 검색할 키워드
    start_date = "2024-01-01"  # 시작 날짜
    end_date = "2024-12-31"    # 종료 날짜
    max_results = 500          # 최대 수집할 게시글 수
    
    # 크롤링 실행
    results = crawler.crawl_all_results(
        keyword=keyword,
        start_date=start_date,
        end_date=end_date,
        max_results=max_results
    )
    
    # 결과 저장
    crawler.save_to_csv(results)
    crawler.save_to_json(results)
    
    # 결과 요약 출력
    print(f"\n=== 크롤링 결과 요약 ===")
    print(f"총 게시글 수: {len(results)}")
    
    total_comments = sum(item.get('comment_count', 0) for item in results)
    total_likes = sum(item.get('sympathy_count', 0) for item in results)
    
    print(f"총 댓글 수: {total_comments}")
    print(f"총 공감 수: {total_likes}")


if __name__ == "__main__":
    main()