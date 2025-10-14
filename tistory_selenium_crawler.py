#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Tistory Blog Crawler with Selenium
티스토리 블로그 크롤러 (Selenium 버전) - 동적 콘텐츠 지원
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import time
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import json
import logging
from typing import List, Dict, Optional
from tqdm import tqdm
import os

class TistorySeleniumCrawler:
    def __init__(self, headless: bool = True, delay: float = 2.0):
        """
        티스토리 Selenium 크롤러 초기화
        
        Args:
            headless: 헤드리스 모드 사용 여부
            delay: 요청 간 지연 시간 (초)
        """
        self.delay = delay
        self.logger = self._setup_logger()
        self.driver = self._setup_driver(headless)
        
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger('TistorySeleniumCrawler')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_driver(self, headless: bool) -> webdriver.Chrome:
        """Chrome WebDriver 설정"""
        try:
            chrome_options = Options()
            
            if headless:
                chrome_options.add_argument('--headless')
            
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # 이미지, CSS 등 불필요한 리소스 차단으로 속도 향상
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values": {
                    "notifications": 2
                }
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.implicitly_wait(10)
            
            self.logger.info("Chrome WebDriver 초기화 완료")
            return driver
            
        except Exception as e:
            self.logger.error(f"WebDriver 초기화 실패: {str(e)}")
            raise
    
    def __del__(self):
        """소멸자 - WebDriver 종료"""
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
            except:
                pass
    
    def search_tistory_posts(self, keyword: str, start_date: str = None, end_date: str = None, 
                           max_pages: int = 10) -> List[Dict]:
        """
        티스토리 검색을 통한 게시글 수집 (Selenium 버전)
        
        Args:
            keyword: 검색 키워드
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
            max_pages: 최대 페이지 수
            
        Returns:
            게시글 정보 리스트
        """
        posts = []
        search_url = f"https://www.tistory.com/search?keyword={keyword}"
        
        self.logger.info(f"키워드 '{keyword}' 검색 시작")
        
        try:
            self.driver.get(search_url)
            time.sleep(self.delay)
            
            for page in range(1, max_pages + 1):
                self.logger.info(f"페이지 {page} 크롤링 중...")
                
                # 페이지 로딩 대기
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".item_post, .list_post li"))
                    )
                except TimeoutException:
                    self.logger.warning(f"페이지 {page} 로딩 타임아웃")
                    break
                
                # 검색 결과 파싱
                post_elements = self.driver.find_elements(By.CSS_SELECTOR, ".item_post, .list_post li")
                
                if not post_elements:
                    self.logger.info(f"페이지 {page}에서 더 이상 결과가 없습니다.")
                    break
                
                page_posts = []
                for element in post_elements:
                    post_info = self._parse_search_result_selenium(element, start_date, end_date)
                    if post_info:
                        page_posts.append(post_info)
                
                posts.extend(page_posts)
                
                # 다음 페이지로 이동
                if page < max_pages and not self._go_to_next_page():
                    break
                
                time.sleep(self.delay)
            
        except Exception as e:
            self.logger.error(f"검색 중 오류 발생: {str(e)}")
        
        self.logger.info(f"총 {len(posts)}개의 게시글을 찾았습니다.")
        return posts
    
    def _parse_search_result_selenium(self, element, start_date: str = None, end_date: str = None) -> Optional[Dict]:
        """
        검색 결과 아이템 파싱 (Selenium 버전)
        """
        try:
            # 제목과 링크
            title_elem = element.find_element(By.CSS_SELECTOR, "a[href*='tistory.com'], .link_post, .tit_post a")
            title = title_elem.text.strip()
            post_url = title_elem.get_attribute('href')
            
            if not title or not post_url:
                return None
            
            # 블로그 정보
            try:
                blog_elem = element.find_element(By.CSS_SELECTOR, ".link_blog, .blog_name a, .name_blog")
                blog_name = blog_elem.text.strip()
                blog_url = blog_elem.get_attribute('href') or ""
            except NoSuchElementException:
                blog_name = "Unknown"
                blog_url = ""
            
            # 날짜 정보
            try:
                date_elem = element.find_element(By.CSS_SELECTOR, ".txt_date, .date, .info_post .date")
                post_date = date_elem.text.strip()
            except NoSuchElementException:
                post_date = ""
            
            # 날짜 필터링
            if start_date or end_date:
                if not self._is_date_in_range(post_date, start_date, end_date):
                    return None
            
            # 미리보기 텍스트
            try:
                preview_elem = element.find_element(By.CSS_SELECTOR, ".txt_post, .desc_post, .summary")
                preview = preview_elem.text.strip()
            except NoSuchElementException:
                preview = ""
            
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
    
    def _go_to_next_page(self) -> bool:
        """다음 페이지로 이동"""
        try:
            next_btn = self.driver.find_element(By.CSS_SELECTOR, ".btn_next, .next, a[href*='page=']")
            if next_btn and next_btn.is_enabled():
                self.driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(self.delay)
                return True
            return False
        except NoSuchElementException:
            return False
    
    def crawl_post_details(self, post_url: str) -> Dict:
        """
        개별 게시글의 상세 정보 크롤링 (Selenium 버전)
        
        Args:
            post_url: 게시글 URL
            
        Returns:
            게시글 상세 정보
        """
        try:
            self.driver.get(post_url)
            time.sleep(self.delay)
            
            # 페이지 로딩 완료 대기
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 동적 콘텐츠 로딩 대기 (댓글 등)
            time.sleep(2)
            
            # 게시글 내용
            content = self._extract_content_selenium()
            
            # 좋아요/공감 수
            like_count = self._extract_like_count_selenium()
            
            # 조회수
            view_count = self._extract_view_count_selenium()
            
            # 댓글 수 및 댓글 정보
            comments_info = self._extract_comments_selenium()
            
            return {
                'content': content,
                'like_count': like_count,
                'view_count': view_count,
                'comment_count': comments_info['count'],
                'comments': comments_info['comments']
            }
            
        except Exception as e:
            self.logger.error(f"게시글 상세 정보 크롤링 오류: {post_url} - {str(e)}")
            return {
                'content': '',
                'like_count': 0,
                'view_count': 0,
                'comment_count': 0,
                'comments': []
            }
    
    def _extract_content_selenium(self) -> str:
        """게시글 내용 추출 (Selenium)"""
        try:
            content_selectors = [
                ".entry-content",
                ".tt_article_useless_p_margin",
                ".contents_style",
                "#content",
                ".post_content",
                ".article_view"
            ]
            
            for selector in content_selectors:
                try:
                    content_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    return content_elem.text.strip()
                except NoSuchElementException:
                    continue
            
            return ""
            
        except Exception:
            return ""
    
    def _extract_like_count_selenium(self) -> int:
        """좋아요/공감 수 추출 (Selenium)"""
        try:
            like_selectors = [
                ".btn_sympathy .txt_num",
                ".area_sympathy .txt_num",
                ".btn_like .num",
                ".like_count",
                ".sympathy_count",
                "[class*='sympathy'] [class*='count']",
                "[class*='like'] [class*='count']"
            ]
            
            for selector in like_selectors:
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    count_text = elem.text.strip()
                    match = re.search(r'\d+', count_text)
                    if match:
                        return int(match.group())
                except NoSuchElementException:
                    continue
            
            return 0
            
        except Exception:
            return 0
    
    def _extract_view_count_selenium(self) -> int:
        """조회수 추출 (Selenium)"""
        try:
            view_selectors = [
                ".view_count",
                ".cnt_view",
                ".num_view",
                "[class*='view'] [class*='count']"
            ]
            
            for selector in view_selectors:
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    count_text = elem.text.strip()
                    match = re.search(r'\d+', count_text)
                    if match:
                        return int(match.group())
                except NoSuchElementException:
                    continue
            
            return 0
            
        except Exception:
            return 0
    
    def _extract_comments_selenium(self) -> Dict:
        """댓글 정보 추출 (Selenium)"""
        try:
            comments = []
            
            # 댓글 로딩 대기 및 더보기 버튼 클릭
            self._load_all_comments()
            
            # 댓글 컨테이너 찾기
            comment_selectors = [
                ".comment_list li",
                ".guestbook_list li",
                "[class*='comment'] li",
                ".reply_list li"
            ]
            
            comment_elements = []
            for selector in comment_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        comment_elements = elements
                        break
                except:
                    continue
            
            for element in comment_elements:
                comment_info = self._parse_comment_selenium(element)
                if comment_info:
                    comments.append(comment_info)
            
            return {
                'count': len(comments),
                'comments': comments
            }
            
        except Exception as e:
            self.logger.error(f"댓글 추출 오류: {str(e)}")
            return {'count': 0, 'comments': []}
    
    def _load_all_comments(self):
        """모든 댓글 로딩 (더보기 버튼 클릭)"""
        try:
            # 댓글 더보기 버튼들
            more_btn_selectors = [
                ".btn_more_comment",
                ".more_comment",
                "[class*='more'][class*='comment']",
                ".btn_more"
            ]
            
            max_clicks = 10  # 무한 루프 방지
            clicks = 0
            
            while clicks < max_clicks:
                clicked = False
                
                for selector in more_btn_selectors:
                    try:
                        btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if btn.is_displayed() and btn.is_enabled():
                            self.driver.execute_script("arguments[0].click();", btn)
                            time.sleep(1)
                            clicked = True
                            clicks += 1
                            break
                    except:
                        continue
                
                if not clicked:
                    break
                    
        except Exception:
            pass
    
    def _parse_comment_selenium(self, element) -> Optional[Dict]:
        """개별 댓글 파싱 (Selenium)"""
        try:
            # 작성자
            author_selectors = [
                ".name",
                ".author",
                ".nick",
                "[class*='name']",
                "[class*='author']"
            ]
            
            author = "익명"
            for selector in author_selectors:
                try:
                    author_elem = element.find_element(By.CSS_SELECTOR, selector)
                    author = author_elem.text.strip()
                    if author:
                        break
                except:
                    continue
            
            # 댓글 내용
            content_selectors = [
                ".comment_content",
                ".content",
                ".text",
                "[class*='content']",
                "[class*='text']"
            ]
            
            content = ""
            for selector in content_selectors:
                try:
                    content_elem = element.find_element(By.CSS_SELECTOR, selector)
                    content = content_elem.text.strip()
                    if content:
                        break
                except:
                    continue
            
            # 날짜
            date_selectors = [
                ".date",
                ".time",
                "[class*='date']",
                "[class*='time']"
            ]
            
            date = ""
            for selector in date_selectors:
                try:
                    date_elem = element.find_element(By.CSS_SELECTOR, selector)
                    date = date_elem.text.strip()
                    if date:
                        break
                except:
                    continue
            
            if not content:
                return None
            
            return {
                'author': author,
                'content': content,
                'date': date
            }
            
        except Exception:
            return None
    
    def _is_date_in_range(self, date_str: str, start_date: str = None, end_date: str = None) -> bool:
        """날짜가 지정된 범위 내에 있는지 확인"""
        try:
            post_date = self._parse_tistory_date(date_str)
            if not post_date:
                return True
            
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
            return True
    
    def _parse_tistory_date(self, date_str: str) -> Optional[datetime]:
        """티스토리 날짜 문자열을 datetime 객체로 변환"""
        try:
            if re.match(r'\d{4}\.\d{1,2}\.\d{1,2}', date_str):
                return datetime.strptime(date_str, '%Y.%m.%d')
            
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
    
    def crawl_keyword_posts(self, keyword: str, start_date: str = None, end_date: str = None,
                          max_pages: int = 10, include_details: bool = True) -> List[Dict]:
        """
        키워드 기반 전체 크롤링 프로세스 (Selenium 버전)
        """
        posts = self.search_tistory_posts(keyword, start_date, end_date, max_pages)
        
        if not include_details or not posts:
            return posts
        
        self.logger.info("게시글 상세 정보 수집 중...")
        
        for i, post in enumerate(tqdm(posts, desc="상세 정보 크롤링")):
            try:
                details = self.crawl_post_details(post['url'])
                post.update(details)
                
                if (i + 1) % 5 == 0:
                    self.logger.info(f"{i + 1}/{len(posts)} 게시글 처리 완료")
                    
            except Exception as e:
                self.logger.error(f"게시글 상세 정보 수집 실패: {post['url']} - {str(e)}")
                continue
        
        return posts
    
    def save_to_csv(self, posts: List[Dict], filename: str = None) -> str:
        """결과를 CSV 파일로 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'tistory_selenium_crawl_{timestamp}.csv'
        
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
    
    def save_to_json(self, posts: List[Dict], filename: str = None) -> str:
        """결과를 JSON 파일로 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'tistory_selenium_crawl_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"결과가 {filename}에 저장되었습니다.")
        return filename


def main():
    """메인 실행 함수"""
    print("🚀 Tistory Selenium 크롤러")
    print("=" * 50)
    
    # 크롤러 설정
    headless = input("헤드리스 모드 사용? (y/N): ").lower().startswith('y')
    crawler = TistorySeleniumCrawler(headless=headless, delay=2.0)
    
    try:
        # 검색 설정
        keyword = input("검색할 키워드를 입력하세요: ")
        start_date = input("시작 날짜 (YYYY-MM-DD, 엔터로 스킵): ").strip() or None
        end_date = input("종료 날짜 (YYYY-MM-DD, 엔터로 스킵): ").strip() or None
        max_pages = int(input("최대 페이지 수 (기본값: 3): ") or 3)
        
        print(f"\n🔍 키워드 '{keyword}' 크롤링을 시작합니다...")
        print(f"📅 기간: {start_date or '제한없음'} ~ {end_date or '제한없음'}")
        print(f"📄 최대 페이지: {max_pages}")
        print("-" * 50)
        
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
            
            # 통계
            total_comments = sum(post.get('comment_count', 0) for post in posts)
            total_likes = sum(post.get('like_count', 0) for post in posts)
            total_views = sum(post.get('view_count', 0) for post in posts)
            
            print(f"\n📊 수집 통계:")
            print(f"   - 총 댓글 수: {total_comments:,}")
            print(f"   - 총 좋아요 수: {total_likes:,}")
            print(f"   - 총 조회수: {total_views:,}")
            
        else:
            print("❌ 검색 결과가 없습니다.")
            
    except KeyboardInterrupt:
        print("\n❌ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {str(e)}")
    finally:
        # WebDriver 정리
        try:
            crawler.driver.quit()
        except:
            pass


if __name__ == "__main__":
    main()