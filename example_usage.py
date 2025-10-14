#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tistory Crawler 사용 예제
"""

from tistory_crawler import TistoryCrawler
from tistory_selenium_crawler import TistorySeleniumCrawler
from datetime import datetime, timedelta

def example_basic_crawler():
    """기본 크롤러 사용 예제"""
    print("=== 기본 크롤러 예제 ===")
    
    # 크롤러 인스턴스 생성
    crawler = TistoryCrawler(delay=1.0)
    
    # 검색 설정
    keyword = "파이썬"
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')  # 30일 전부터
    end_date = datetime.now().strftime('%Y-%m-%d')  # 오늘까지
    
    print(f"키워드: {keyword}")
    print(f"기간: {start_date} ~ {end_date}")
    
    # 크롤링 실행
    posts = crawler.crawl_keyword_posts(
        keyword=keyword,
        start_date=start_date,
        end_date=end_date,
        max_pages=2,
        include_details=True
    )
    
    if posts:
        print(f"수집된 게시글 수: {len(posts)}")
        
        # 결과 저장
        csv_file = crawler.save_to_csv(posts, f"basic_crawl_{keyword}.csv")
        json_file = crawler.save_to_json(posts, f"basic_crawl_{keyword}.json")
        
        print(f"CSV 파일: {csv_file}")
        print(f"JSON 파일: {json_file}")
        
        # 첫 번째 게시글 정보 출력
        if posts:
            first_post = posts[0]
            print(f"\n첫 번째 게시글:")
            print(f"  제목: {first_post.get('title', 'N/A')}")
            print(f"  블로그: {first_post.get('blog_name', 'N/A')}")
            print(f"  좋아요: {first_post.get('like_count', 0)}")
            print(f"  댓글 수: {first_post.get('comment_count', 0)}")
    
    return posts

def example_selenium_crawler():
    """Selenium 크롤러 사용 예제"""
    print("\n=== Selenium 크롤러 예제 ===")
    
    # 크롤러 인스턴스 생성 (헤드리스 모드)
    crawler = TistorySeleniumCrawler(headless=True, delay=2.0)
    
    try:
        # 검색 설정
        keyword = "블로그"
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')  # 7일 전부터
        
        print(f"키워드: {keyword}")
        print(f"기간: {start_date} ~ 오늘")
        
        # 크롤링 실행
        posts = crawler.crawl_keyword_posts(
            keyword=keyword,
            start_date=start_date,
            max_pages=1,
            include_details=True
        )
        
        if posts:
            print(f"수집된 게시글 수: {len(posts)}")
            
            # 결과 저장
            csv_file = crawler.save_to_csv(posts, f"selenium_crawl_{keyword}.csv")
            json_file = crawler.save_to_json(posts, f"selenium_crawl_{keyword}.json")
            
            print(f"CSV 파일: {csv_file}")
            print(f"JSON 파일: {json_file}")
            
            # 통계 출력
            total_comments = sum(post.get('comment_count', 0) for post in posts)
            total_likes = sum(post.get('like_count', 0) for post in posts)
            
            print(f"\n통계:")
            print(f"  총 댓글 수: {total_comments}")
            print(f"  총 좋아요 수: {total_likes}")
        
        return posts
        
    finally:
        # WebDriver 정리
        crawler.driver.quit()

def example_custom_analysis(posts):
    """수집된 데이터 분석 예제"""
    if not posts:
        return
    
    print("\n=== 데이터 분석 예제 ===")
    
    # 블로그별 게시글 수
    blog_counts = {}
    for post in posts:
        blog_name = post.get('blog_name', 'Unknown')
        blog_counts[blog_name] = blog_counts.get(blog_name, 0) + 1
    
    print("블로그별 게시글 수:")
    for blog, count in sorted(blog_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {blog}: {count}개")
    
    # 좋아요 수 상위 게시글
    posts_with_likes = [p for p in posts if p.get('like_count', 0) > 0]
    if posts_with_likes:
        top_liked = sorted(posts_with_likes, key=lambda x: x.get('like_count', 0), reverse=True)[:3]
        print(f"\n좋아요 수 상위 게시글:")
        for i, post in enumerate(top_liked, 1):
            print(f"  {i}. {post.get('title', 'N/A')[:50]}... (좋아요: {post.get('like_count', 0)})")
    
    # 댓글 수 상위 게시글
    posts_with_comments = [p for p in posts if p.get('comment_count', 0) > 0]
    if posts_with_comments:
        top_commented = sorted(posts_with_comments, key=lambda x: x.get('comment_count', 0), reverse=True)[:3]
        print(f"\n댓글 수 상위 게시글:")
        for i, post in enumerate(top_commented, 1):
            print(f"  {i}. {post.get('title', 'N/A')[:50]}... (댓글: {post.get('comment_count', 0)})")

def main():
    """메인 실행 함수"""
    print("Tistory 크롤러 사용 예제")
    print("=" * 50)
    
    # 기본 크롤러 예제
    basic_posts = example_basic_crawler()
    
    # Selenium 크롤러 예제
    selenium_posts = example_selenium_crawler()
    
    # 데이터 분석 예제
    all_posts = basic_posts + (selenium_posts or [])
    example_custom_analysis(all_posts)
    
    print("\n✅ 모든 예제가 완료되었습니다.")

if __name__ == "__main__":
    main()