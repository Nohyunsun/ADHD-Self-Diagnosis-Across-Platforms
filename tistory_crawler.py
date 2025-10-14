#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tistory Blog Crawler
티스토리 블로그 크롤러 - 키워드 검색을 통한 게시글, 댓글, 좋아요 수 수집
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs
from fake_useragent import UserAgent
import json
import logging
from typing import List, Dict, Optional
from tqdm import tqdm
import os

class TistoryCrawler:
    def __init__(self, delay: float = 1.0):
        """
        티스토리 크롤러 초기화
        
        Args:
            delay: 요청 간 지연 시간 (초)
        """
        self.session = requests.Session()
        self.ua = UserAgent()
        self.delay = delay
        self.logger = self._setup_logger()
        
        # 기본 헤더 설정
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger('TistoryCrawler')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _make_request(self, url: str, params: Dict = None) -> Optional[BeautifulSoup]:
        """
        HTTP 요청 및 BeautifulSoup 객체 반환
        
        Args:
            url: 요청할 URL
            params: 쿼리 파라미터
            
        Returns:
            BeautifulSoup 객체 또는 None
        """
        try:
            time.sleep(self.delay)
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # 인코딩 설정
            if response.encoding == 'ISO-8859-1':
                response.encoding = 'utf-8'
            
            return BeautifulSoup(response.text, 'lxml')
            
        except Exception as e:
            self.logger.error(f"요청 실패: {url} - {str(e)}")
            return None
    
    def search_tistory_posts(self, keyword: str, start_date: str = None, end_date: str = None, 
                           max_pages: int = 10) -> List[Dict]:
        """
        티스토리 검색을 통한 게시글 수집
        
        Args:
            keyword: 검색 키워드
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
            max_pages: 최대 페이지 수
            
        Returns:
            게시글 정보 리스트
        """
        posts = []
        search_url = "https://www.tistory.com/search"
        
        self.logger.info(f"키워드 '{keyword}' 검색 시작")
        
        for page in range(1, max_pages + 1):
            self.logger.info(f"페이지 {page} 크롤링 중...")
            
            params = {
                'keyword': keyword,
                'page': page
            }
            
            soup = self._make_request(search_url, params)
            if not soup:
                break
            
            # 검색 결과 파싱
            post_items = soup.find_all('div', class_='item_post')
            
            if not post_items:
                self.logger.info(f"페이지 {page}에서 더 이상 결과가 없습니다.")
                break
            
            for item in post_items:
                post_info = self._parse_search_result(item, start_date, end_date)
                if post_info:
                    posts.append(post_info)
            
            # 다음 페이지가 있는지 확인
            if not self._has_next_page(soup):
                break
        
        self.logger.info(f"총 {len(posts)}개의 게시글을 찾았습니다.")
        return posts
    
    def _parse_search_result(self, item, start_date: str = None, end_date: str = None) -> Optional[Dict]:
        """
        검색 결과 아이템 파싱
        
        Args:
            item: BeautifulSoup 검색 결과 아이템
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            게시글 정보 딕셔너리
        """
        try:
            # 제목과 링크
            title_elem = item.find('a', class_='link_post')
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            post_url = title_elem.get('href')
            
            # 블로그 정보
            blog_elem = item.find('a', class_='link_blog')
            blog_name = blog_elem.get_text(strip=True) if blog_elem else "Unknown"
            blog_url = blog_elem.get('href') if blog_elem else ""
            
            # 날짜 정보
            date_elem = item.find('span', class_='txt_date')
            post_date = date_elem.get_text(strip=True) if date_elem else ""
            
            # 날짜 필터링
            if start_date or end_date:
                if not self._is_date_in_range(post_date, start_date, end_date):
                    return None
            
            # 미리보기 텍스트
            preview_elem = item.find('p', class_='txt_post')
            preview = preview_elem.get_text(strip=True) if preview_elem else ""
            
            return {
                'title': title,
                'url': post_url,
                'blog_name': blog_name,
                'blog_url': blog_url,
                'date': post_date,
                'preview': preview,
                'crawled_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"검색 결과 파싱 오류: {str(e)}")
            return None
    
    def _has_next_page(self, soup: BeautifulSoup) -> bool:
        """다음 페이지 존재 여부 확인"""
        next_btn = soup.find('a', class_='btn_next')
        return next_btn is not None and 'disabled' not in next_btn.get('class', [])
    
    def _is_date_in_range(self, date_str: str, start_date: str = None, end_date: str = None) -> bool:
        """날짜가 지정된 범위 내에 있는지 확인"""
        try:
            # 티스토리 날짜 형식 파싱 (예: "2024.01.15", "1일 전", "1주 전" 등)
            post_date = self._parse_tistory_date(date_str)
            if not post_date:
                return True  # 날짜를 파싱할 수 없으면 포함
            
            if start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                if post_date < start_dt:
                    return False
            
            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                if post_date > end_dt:
                    return False
            
            return True
            
        except Exception:
            return True  # 오류 시 포함
    
    def _parse_tistory_date(self, date_str: str) -> Optional[datetime]:
        """티스토리 날짜 문자열을 datetime 객체로 변환"""
        try:
            # "YYYY.MM.DD" 형식
            if re.match(r'\d{4}\.\d{1,2}\.\d{1,2}', date_str):
                return datetime.strptime(date_str, '%Y.%m.%d')
            
            # "N일 전", "N주 전", "N개월 전" 형식
            now = datetime.now()
            
            if '일 전' in date_str:
                days = int(re.search(r'(\d+)일 전', date_str).group(1))
                return now - timedelta(days=days)
            elif '주 전' in date_str:
                weeks = int(re.search(r'(\d+)주 전', date_str).group(1))
                return now - timedelta(weeks=weeks)
            elif '개월 전' in date_str:
                months = int(re.search(r'(\d+)개월 전', date_str).group(1))
                return now - timedelta(days=months * 30)
            elif '년 전' in date_str:
                years = int(re.search(r'(\d+)년 전', date_str).group(1))
                return now - timedelta(days=years * 365)
            
            return None
            
        except Exception:
            return None
    
    def crawl_post_details(self, post_url: str) -> Dict:
        """
        개별 게시글의 상세 정보 크롤링
        
        Args:
            post_url: 게시글 URL
            
        Returns:
            게시글 상세 정보
        """
        soup = self._make_request(post_url)
        if not soup:
            return {}
        
        try:
            # 게시글 내용
            content_elem = soup.find('div', class_='entry-content') or soup.find('div', class_='tt_article_useless_p_margin')
            content = content_elem.get_text(strip=True) if content_elem else ""
            
            # 좋아요/공감 수
            like_count = self._extract_like_count(soup)
            
            # 댓글 수 및 댓글 정보
            comments_info = self._extract_comments(soup, post_url)
            
            # 조회수
            view_count = self._extract_view_count(soup)
            
            return {
                'content': content,
                'like_count': like_count,
                'view_count': view_count,
                'comment_count': comments_info['count'],
                'comments': comments_info['comments']
            }
            
        except Exception as e:
            self.logger.error(f"게시글 상세 정보 크롤링 오류: {post_url} - {str(e)}")
            return {}
    
    def _extract_like_count(self, soup: BeautifulSoup) -> int:
        """좋아요/공감 수 추출"""
        try:
            # 다양한 좋아요 버튼 셀렉터 시도
            selectors = [
                '.btn_sympathy .txt_num',
                '.area_sympathy .txt_num',
                '.btn_like .num',
                '.like_count',
                '.sympathy_count'
            ]
            
            for selector in selectors:
                elem = soup.select_one(selector)
                if elem:
                    count_text = elem.get_text(strip=True)
                    return int(re.search(r'\d+', count_text).group()) if re.search(r'\d+', count_text) else 0
            
            return 0
            
        except Exception:
            return 0
    
    def _extract_view_count(self, soup: BeautifulSoup) -> int:
        """조회수 추출"""
        try:
            # 조회수 관련 셀렉터
            selectors = [
                '.view_count',
                '.cnt_view',
                '.num_view'
            ]
            
            for selector in selectors:
                elem = soup.select_one(selector)
                if elem:
                    count_text = elem.get_text(strip=True)
                    return int(re.search(r'\d+', count_text).group()) if re.search(r'\d+', count_text) else 0
            
            return 0
            
        except Exception:
            return 0
    
    def _extract_comments(self, soup: BeautifulSoup, post_url: str) -> Dict:
        """댓글 정보 추출"""
        try:
            comments = []
            
            # 댓글 컨테이너 찾기
            comment_containers = soup.find_all(['div', 'li'], class_=re.compile(r'comment|reply'))
            
            for container in comment_containers:
                comment_info = self._parse_comment(container)
                if comment_info:
                    comments.append(comment_info)
            
            # 댓글이 AJAX로 로드되는 경우를 위한 추가 처리
            if not comments:
                comments = self._extract_ajax_comments(post_url)
            
            return {
                'count': len(comments),
                'comments': comments
            }
            
        except Exception as e:
            self.logger.error(f"댓글 추출 오류: {str(e)}")
            return {'count': 0, 'comments': []}
    
    def _parse_comment(self, container) -> Optional[Dict]:
        """개별 댓글 파싱"""
        try:
            # 작성자
            author_elem = container.find(['span', 'strong'], class_=re.compile(r'name|author|nick'))
            author = author_elem.get_text(strip=True) if author_elem else "익명"
            
            # 댓글 내용
            content_elem = container.find(['p', 'div'], class_=re.compile(r'content|text|comment'))
            content = content_elem.get_text(strip=True) if content_elem else ""
            
            # 날짜
            date_elem = container.find(['span', 'time'], class_=re.compile(r'date|time'))
            date = date_elem.get_text(strip=True) if date_elem else ""
            
            if not content:
                return None
            
            return {
                'author': author,
                'content': content,
                'date': date
            }
            
        except Exception:
            return None
    
    def _extract_ajax_comments(self, post_url: str) -> List[Dict]:
        """AJAX로 로드되는 댓글 추출 (기본 구현)"""
        # 실제 구현에서는 각 블로그의 댓글 API를 분석해야 함
        return []
    
    def crawl_keyword_posts(self, keyword: str, start_date: str = None, end_date: str = None,
                          max_pages: int = 10, include_details: bool = True) -> List[Dict]:
        """
        키워드 기반 전체 크롤링 프로세스
        
        Args:
            keyword: 검색 키워드
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
            max_pages: 최대 페이지 수
            include_details: 상세 정보 포함 여부
            
        Returns:
            완전한 게시글 정보 리스트
        """
        # 1단계: 검색을 통한 게시글 목록 수집
        posts = self.search_tistory_posts(keyword, start_date, end_date, max_pages)
        
        if not include_details:
            return posts
        
        # 2단계: 각 게시글의 상세 정보 수집
        self.logger.info("게시글 상세 정보 수집 중...")
        
        for i, post in enumerate(tqdm(posts, desc="상세 정보 크롤링")):
            try:
                details = self.crawl_post_details(post['url'])
                post.update(details)
                
                # 진행률 로그
                if (i + 1) % 10 == 0:
                    self.logger.info(f"{i + 1}/{len(posts)} 게시글 처리 완료")
                    
            except Exception as e:
                self.logger.error(f"게시글 상세 정보 수집 실패: {post['url']} - {str(e)}")
                continue
        
        return posts
    
    def save_to_csv(self, posts: List[Dict], filename: str = None):
        """결과를 CSV 파일로 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'tistory_crawl_{timestamp}.csv'
        
        # 댓글 정보를 별도 처리
        flattened_data = []
        
        for post in posts:
            base_data = {
                'title': post.get('title', ''),
                'url': post.get('url', ''),
                'blog_name': post.get('blog_name', ''),
                'blog_url': post.get('blog_url', ''),
                'date': post.get('date', ''),
                'content': post.get('content', ''),
                'like_count': post.get('like_count', 0),
                'view_count': post.get('view_count', 0),
                'comment_count': post.get('comment_count', 0),
                'preview': post.get('preview', ''),
                'crawled_at': post.get('crawled_at', '')
            }
            
            # 댓글이 있는 경우 각 댓글을 별도 행으로 추가
            comments = post.get('comments', [])
            if comments:
                for comment in comments:
                    row_data = base_data.copy()
                    row_data.update({
                        'comment_author': comment.get('author', ''),
                        'comment_content': comment.get('content', ''),
                        'comment_date': comment.get('date', '')
                    })
                    flattened_data.append(row_data)
            else:
                # 댓글이 없는 경우 기본 데이터만 추가
                base_data.update({
                    'comment_author': '',
                    'comment_content': '',
                    'comment_date': ''
                })
                flattened_data.append(base_data)
        
        df = pd.DataFrame(flattened_data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        self.logger.info(f"결과가 {filename}에 저장되었습니다.")
        
        return filename
    
    def save_to_json(self, posts: List[Dict], filename: str = None):
        """결과를 JSON 파일로 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'tistory_crawl_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"결과가 {filename}에 저장되었습니다.")
        return filename


def main():
    """메인 실행 함수"""
    # 크롤러 인스턴스 생성
    crawler = TistoryCrawler(delay=1.5)  # 1.5초 지연
    
    # 검색 설정
    keyword = input("검색할 키워드를 입력하세요: ")
    start_date = input("시작 날짜 (YYYY-MM-DD, 엔터로 스킵): ").strip() or None
    end_date = input("종료 날짜 (YYYY-MM-DD, 엔터로 스킵): ").strip() or None
    max_pages = int(input("최대 페이지 수 (기본값: 5): ") or 5)
    
    print(f"\n키워드 '{keyword}' 크롤링을 시작합니다...")
    print(f"기간: {start_date or '제한없음'} ~ {end_date or '제한없음'}")
    print(f"최대 페이지: {max_pages}")
    print("-" * 50)
    
    try:
        # 크롤링 실행
        posts = crawler.crawl_keyword_posts(
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
            max_pages=max_pages,
            include_details=True
        )
        
        if posts:
            print(f"\n✅ 총 {len(posts)}개의 게시글을 수집했습니다.")
            
            # 결과 저장
            csv_file = crawler.save_to_csv(posts)
            json_file = crawler.save_to_json(posts)
            
            print(f"📄 CSV 파일: {csv_file}")
            print(f"📄 JSON 파일: {json_file}")
            
            # 간단한 통계
            total_comments = sum(post.get('comment_count', 0) for post in posts)
            total_likes = sum(post.get('like_count', 0) for post in posts)
            
            print(f"\n📊 수집 통계:")
            print(f"   - 총 댓글 수: {total_comments:,}")
            print(f"   - 총 좋아요 수: {total_likes:,}")
            
        else:
            print("❌ 검색 결과가 없습니다.")
            
    except KeyboardInterrupt:
        print("\n❌ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {str(e)}")


if __name__ == "__main__":
    main()