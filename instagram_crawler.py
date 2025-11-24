"""
Instagram 키워드 검색 및 데이터 크롤링 시스템

이 모듈은 인스타그램에서 키워드 검색을 통해 게시글과 댓글 데이터를 수집합니다.
- 게시글 정보: 닉네임, 내용, 좋아요 수, 댓글 수, 공유 수
- 댓글 정보: 댓글 내용, 작성자, 작성일
- 기간 필터링 지원
- JSON/CSV 형식으로 데이터 저장
"""

import json
import csv
import time
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import logging

import instaloader
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
import pandas as pd


@dataclass
class InstagramPost:
    """인스타그램 게시글 데이터 구조"""
    post_id: str
    username: str
    display_name: str
    caption: str
    likes_count: int
    comments_count: int
    shares_count: int = 0  # 인스타그램은 공유 수를 직접 제공하지 않음
    post_date: str
    post_url: str
    hashtags: List[str]
    mentions: List[str]
    location: Optional[str] = None
    media_type: str = "photo"  # photo, video, carousel
    media_urls: List[str] = None

    def __post_init__(self):
        if self.media_urls is None:
            self.media_urls = []


@dataclass
class InstagramComment:
    """인스타그램 댓글 데이터 구조"""
    comment_id: str
    post_id: str
    username: str
    display_name: str
    text: str
    likes_count: int
    comment_date: str
    is_reply: bool = False
    parent_comment_id: Optional[str] = None
    replies_count: int = 0


class InstagramCrawler:
    """인스타그램 크롤링 메인 클래스"""
    
    def __init__(self, username: str = None, password: str = None, headless: bool = True):
        """
        인스타그램 크롤러 초기화
        
        Args:
            username: 인스타그램 사용자명 (로그인 필요시)
            password: 인스타그램 비밀번호 (로그인 필요시)
            headless: 브라우저를 백그라운드에서 실행할지 여부
        """
        self.username = username
        self.password = password
        self.headless = headless
        self.driver = None
        self.loader = None
        self.session = requests.Session()
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # User Agent 설정
        self.ua = UserAgent()
        
    def setup_driver(self) -> webdriver.Chrome:
        """Selenium WebDriver 설정"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(f"--user-agent={self.ua.random}")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def setup_instaloader(self) -> instaloader.Instaloader:
        """Instaloader 설정"""
        loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=True,
            save_metadata=False,
            compress_json=False
        )
        
        # 로그인 (선택사항)
        if self.username and self.password:
            try:
                loader.login(self.username, self.password)
                self.logger.info(f"Successfully logged in as {self.username}")
            except Exception as e:
                self.logger.warning(f"Login failed: {e}")
                self.logger.info("Continuing without login (limited functionality)")
        
        return loader
    
    def initialize(self):
        """크롤러 초기화"""
        try:
            self.driver = self.setup_driver()
            self.loader = self.setup_instaloader()
        except Exception as e:
            self.logger.error(f"Failed to initialize crawler: {e}")
            raise
    
    def cleanup(self):
        """리소스 정리"""
        if self.driver:
            self.driver.quit()
    
    def search_hashtag_posts(self, hashtag: str, max_posts: int = 50, days_back: int = 30) -> List[InstagramPost]:
        """
        해시태그로 게시글 검색
        
        Args:
            hashtag: 검색할 해시태그 (# 없이)
            max_posts: 최대 수집할 게시글 수
            days_back: 몇 일 전까지의 게시글을 수집할지
            
        Returns:
            InstagramPost 객체 리스트
        """
        posts = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        try:
            hashtag_obj = instaloader.Hashtag.from_name(self.loader.context, hashtag)
            
            for post in hashtag_obj.get_posts():
                if len(posts) >= max_posts:
                    break
                
                # 날짜 필터링
                if post.date < cutoff_date:
                    continue
                
                try:
                    instagram_post = self._extract_post_data(post)
                    posts.append(instagram_post)
                    self.logger.info(f"Collected post from @{instagram_post.username}")
                    
                    # API 호출 제한을 위한 지연
                    time.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Error extracting post data: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error searching hashtag {hashtag}: {e}")
        
        return posts
    
    def search_keyword_posts(self, keyword: str, max_posts: int = 50, days_back: int = 30) -> List[InstagramPost]:
        """
        키워드로 게시글 검색 (Selenium 사용)
        
        Args:
            keyword: 검색할 키워드
            max_posts: 최대 수집할 게시글 수
            days_back: 몇 일 전까지의 게시글을 수집할지
            
        Returns:
            InstagramPost 객체 리스트
        """
        posts = []
        
        try:
            # 인스타그램 검색 페이지로 이동
            search_url = f"https://www.instagram.com/explore/tags/{keyword.replace(' ', '').replace('#', '')}/"
            self.driver.get(search_url)
            time.sleep(3)
            
            # 게시글 링크 수집
            post_links = self._collect_post_links(max_posts)
            
            # 각 게시글 데이터 추출
            for link in post_links[:max_posts]:
                try:
                    post_data = self._extract_post_data_selenium(link, days_back)
                    if post_data:
                        posts.append(post_data)
                        self.logger.info(f"Collected post from @{post_data.username}")
                    
                    time.sleep(2)  # 요청 간격 조절
                    
                except Exception as e:
                    self.logger.error(f"Error extracting post from {link}: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error searching keyword {keyword}: {e}")
        
        return posts
    
    def _collect_post_links(self, max_posts: int) -> List[str]:
        """게시글 링크 수집"""
        links = []
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while len(links) < max_posts:
            # 페이지 스크롤
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 게시글 링크 찾기
            post_elements = self.driver.find_elements(By.CSS_SELECTOR, "article a[href*='/p/']")
            
            for element in post_elements:
                href = element.get_attribute('href')
                if href and href not in links:
                    links.append(href)
            
            # 새로운 콘텐츠가 로드되었는지 확인
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        return links[:max_posts]
    
    def _extract_post_data(self, post) -> InstagramPost:
        """Instaloader Post 객체에서 데이터 추출"""
        # 해시태그와 멘션 추출
        hashtags = re.findall(r'#(\w+)', post.caption or '')
        mentions = re.findall(r'@(\w+)', post.caption or '')
        
        return InstagramPost(
            post_id=post.shortcode,
            username=post.owner_username,
            display_name=post.owner_profile.full_name if hasattr(post.owner_profile, 'full_name') else post.owner_username,
            caption=post.caption or '',
            likes_count=post.likes,
            comments_count=post.comments,
            shares_count=0,  # 인스타그램은 공유 수를 제공하지 않음
            post_date=post.date.isoformat(),
            post_url=f"https://www.instagram.com/p/{post.shortcode}/",
            hashtags=hashtags,
            mentions=mentions,
            location=post.location.name if post.location else None,
            media_type="video" if post.is_video else "photo",
            media_urls=[post.url]
        )
    
    def _extract_post_data_selenium(self, post_url: str, days_back: int) -> Optional[InstagramPost]:
        """Selenium을 사용하여 게시글 데이터 추출"""
        try:
            self.driver.get(post_url)
            time.sleep(3)
            
            # 게시글 ID 추출
            post_id = post_url.split('/p/')[-1].rstrip('/')
            
            # 사용자명 추출
            username_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "header a"))
            )
            username = username_element.text
            
            # 게시글 내용 추출
            try:
                caption_element = self.driver.find_element(By.CSS_SELECTOR, "article div[data-testid='post-caption'] span")
                caption = caption_element.text
            except:
                caption = ""
            
            # 좋아요 수 추출
            try:
                likes_element = self.driver.find_element(By.CSS_SELECTOR, "section button span")
                likes_text = likes_element.text
                likes_count = self._parse_count(likes_text)
            except:
                likes_count = 0
            
            # 댓글 수는 별도로 계산 (아래에서 구현)
            comments_count = 0
            
            # 날짜 추출 (간단한 구현)
            post_date = datetime.now().isoformat()
            
            # 해시태그와 멘션 추출
            hashtags = re.findall(r'#(\w+)', caption)
            mentions = re.findall(r'@(\w+)', caption)
            
            return InstagramPost(
                post_id=post_id,
                username=username,
                display_name=username,
                caption=caption,
                likes_count=likes_count,
                comments_count=comments_count,
                shares_count=0,
                post_date=post_date,
                post_url=post_url,
                hashtags=hashtags,
                mentions=mentions
            )
            
        except Exception as e:
            self.logger.error(f"Error extracting post data from {post_url}: {e}")
            return None
    
    def extract_comments(self, post: InstagramPost, max_comments: int = 100) -> List[InstagramComment]:
        """게시글의 댓글 추출"""
        comments = []
        
        try:
            # Instaloader를 사용하여 댓글 추출
            insta_post = instaloader.Post.from_shortcode(self.loader.context, post.post_id)
            
            comment_count = 0
            for comment in insta_post.get_comments():
                if comment_count >= max_comments:
                    break
                
                instagram_comment = InstagramComment(
                    comment_id=str(comment.id),
                    post_id=post.post_id,
                    username=comment.owner.username,
                    display_name=comment.owner.full_name or comment.owner.username,
                    text=comment.text,
                    likes_count=comment.likes_count,
                    comment_date=comment.created_at.isoformat(),
                    is_reply=False,
                    replies_count=0
                )
                
                comments.append(instagram_comment)
                comment_count += 1
                
                # 대댓글 처리
                for reply in comment.answers:
                    if comment_count >= max_comments:
                        break
                    
                    instagram_reply = InstagramComment(
                        comment_id=str(reply.id),
                        post_id=post.post_id,
                        username=reply.owner.username,
                        display_name=reply.owner.full_name or reply.owner.username,
                        text=reply.text,
                        likes_count=reply.likes_count,
                        comment_date=reply.created_at.isoformat(),
                        is_reply=True,
                        parent_comment_id=str(comment.id)
                    )
                    
                    comments.append(instagram_reply)
                    comment_count += 1
                
                time.sleep(0.5)  # API 호출 제한
            
            # 게시글의 댓글 수 업데이트
            post.comments_count = len([c for c in comments if not c.is_reply])
            
        except Exception as e:
            self.logger.error(f"Error extracting comments for post {post.post_id}: {e}")
        
        return comments
    
    def _parse_count(self, count_text: str) -> int:
        """좋아요/댓글 수 텍스트를 숫자로 변환"""
        if not count_text:
            return 0
        
        count_text = count_text.lower().replace(',', '').replace(' ', '')
        
        if 'k' in count_text:
            return int(float(count_text.replace('k', '')) * 1000)
        elif 'm' in count_text:
            return int(float(count_text.replace('m', '')) * 1000000)
        else:
            try:
                return int(count_text)
            except:
                return 0
    
    def crawl_keyword(self, keyword: str, max_posts: int = 50, max_comments_per_post: int = 100, 
                     days_back: int = 30, save_format: str = "json", max_retries: int = 3) -> Dict[str, Any]:
        """
        키워드로 인스타그램 데이터 크롤링
        
        Args:
            keyword: 검색할 키워드
            max_posts: 최대 수집할 게시글 수
            max_comments_per_post: 게시글당 최대 댓글 수
            days_back: 몇 일 전까지의 게시글을 수집할지
            save_format: 저장 형식 ("json" 또는 "csv")
            max_retries: 최대 재시도 횟수
            
        Returns:
            수집된 데이터 딕셔너리
        """
        self.logger.info(f"Starting crawl for keyword: {keyword}")
        
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                # 초기화
                self.initialize()
                
                # 게시글 수집
                posts = []
                
                # 해시태그로 검색 시도
                if keyword.startswith('#'):
                    hashtag = keyword[1:]
                    posts = self.search_hashtag_posts(hashtag, max_posts, days_back)
                else:
                    # 일반 키워드로 검색
                    posts = self.search_keyword_posts(keyword, max_posts, days_back)
                
                self.logger.info(f"Collected {len(posts)} posts")
                
                # 댓글 수집
                all_comments = []
                for i, post in enumerate(posts):
                    try:
                        self.logger.info(f"Extracting comments for post {i+1}/{len(posts)}")
                        comments = self.extract_comments(post, max_comments_per_post)
                        all_comments.extend(comments)
                        time.sleep(1)
                    except Exception as e:
                        self.logger.warning(f"Failed to extract comments for post {post.post_id}: {e}")
                        continue
                
                self.logger.info(f"Collected {len(all_comments)} comments")
                
                # 데이터 저장
                result = {
                    'keyword': keyword,
                    'crawl_date': datetime.now().isoformat(),
                    'posts': [asdict(post) for post in posts],
                    'comments': [asdict(comment) for comment in all_comments],
                    'summary': {
                        'total_posts': len(posts),
                        'total_comments': len(all_comments),
                        'total_likes': sum(post.likes_count for post in posts),
                        'date_range': f"Last {days_back} days"
                    }
                }
                
                # 파일 저장
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                try:
                    if save_format.lower() == "json":
                        filename = f"instagram_data_{keyword.replace(' ', '_').replace('#', '')}_{timestamp}.json"
                        self.save_to_json(result, filename)
                    elif save_format.lower() == "csv":
                        posts_filename = f"instagram_posts_{keyword.replace(' ', '_').replace('#', '')}_{timestamp}.csv"
                        comments_filename = f"instagram_comments_{keyword.replace(' ', '_').replace('#', '')}_{timestamp}.csv"
                        self.save_to_csv(posts, all_comments, posts_filename, comments_filename)
                except Exception as e:
                    self.logger.error(f"Failed to save data: {e}")
                    # 저장 실패해도 결과는 반환
                
                return result
                
            except Exception as e:
                retry_count += 1
                last_error = e
                self.logger.error(f"Crawl attempt {retry_count} failed for keyword '{keyword}': {e}")
                
                if retry_count < max_retries:
                    wait_time = retry_count * 10  # 재시도 간격 증가
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                
                # 리소스 정리 후 재시도
                try:
                    self.cleanup()
                except:
                    pass
            
            finally:
                try:
                    self.cleanup()
                except:
                    pass
        
        # 모든 재시도 실패
        self.logger.error(f"All {max_retries} attempts failed for keyword '{keyword}'. Last error: {last_error}")
        raise Exception(f"Failed to crawl keyword '{keyword}' after {max_retries} attempts: {last_error}")
    
    def save_to_json(self, data: Dict[str, Any], filename: str):
        """JSON 형식으로 데이터 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.logger.info(f"Data saved to {filename}")
    
    def save_to_csv(self, posts: List[InstagramPost], comments: List[InstagramComment], 
                   posts_filename: str, comments_filename: str):
        """CSV 형식으로 데이터 저장"""
        # 게시글 데이터 저장
        posts_df = pd.DataFrame([asdict(post) for post in posts])
        posts_df.to_csv(posts_filename, index=False, encoding='utf-8-sig')
        
        # 댓글 데이터 저장
        if comments:
            comments_df = pd.DataFrame([asdict(comment) for comment in comments])
            comments_df.to_csv(comments_filename, index=False, encoding='utf-8-sig')
        
        self.logger.info(f"Data saved to {posts_filename} and {comments_filename}")


def main():
    """대화형 크롤링 실행"""
    print("=== Instagram 키워드 크롤러 ===")
    print()
    
    # 사용자 입력
    keyword = input("검색할 키워드를 입력하세요: ").strip()
    if not keyword:
        print("키워드가 입력되지 않았습니다.")
        return
    
    try:
        max_posts = int(input("최대 게시글 수 (기본값: 50): ") or "50")
        max_comments = int(input("게시글당 최대 댓글 수 (기본값: 100): ") or "100")
        days_back = int(input("검색 기간 (일, 기본값: 30): ") or "30")
    except ValueError:
        print("잘못된 숫자 입력입니다. 기본값을 사용합니다.")
        max_posts, max_comments, days_back = 50, 100, 30
    
    save_format = input("저장 형식 (json/csv, 기본값: json): ").lower() or "json"
    if save_format not in ["json", "csv"]:
        save_format = "json"
    
    # 로그인 정보 (선택사항)
    print("\n로그인 정보 (선택사항, 더 많은 데이터 수집 가능):")
    username = input("Instagram 사용자명 (선택사항): ").strip()
    password = ""
    if username:
        import getpass
        password = getpass.getpass("Instagram 비밀번호: ")
    
    print(f"\n크롤링 시작: {keyword}")
    print(f"설정: 게시글 {max_posts}개, 댓글 {max_comments}개/게시글, 최근 {days_back}일")
    print("=" * 50)
    
    # 크롤링 실행
    crawler = InstagramCrawler(username=username, password=password)
    
    try:
        result = crawler.crawl_keyword(
            keyword=keyword,
            max_posts=max_posts,
            max_comments_per_post=max_comments,
            days_back=days_back,
            save_format=save_format
        )
        
        print("\n=== 크롤링 완료 ===")
        print(f"수집된 게시글: {result['summary']['total_posts']}개")
        print(f"수집된 댓글: {result['summary']['total_comments']}개")
        print(f"총 좋아요: {result['summary']['total_likes']:,}개")
        
    except Exception as e:
        print(f"\n크롤링 중 오류 발생: {e}")
        logging.error(f"Crawling error: {e}", exc_info=True)


if __name__ == "__main__":
    main()