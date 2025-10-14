"""
네이버 블로그 크롤러 사용 예시
"""

import os
from datetime import datetime, timedelta
from naver_blog_crawler import NaverBlogCrawler
from config import NAVER_API_CONFIG, CRAWLING_CONFIG, OUTPUT_CONFIG

def example_basic_search():
    """기본 검색 예시"""
    print("=== 기본 검색 예시 ===")
    
    # API 키 설정 (실제 사용시 config.py 또는 환경변수에서 가져오기)
    client_id = NAVER_API_CONFIG["CLIENT_ID"]
    client_secret = NAVER_API_CONFIG["CLIENT_SECRET"]
    
    # 실제 API 키가 설정되지 않은 경우 환경변수에서 가져오기
    if client_id == "YOUR_CLIENT_ID_HERE":
        client_id = os.getenv("NAVER_CLIENT_ID")
        client_secret = os.getenv("NAVER_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("네이버 API 키를 설정해주세요!")
        print("1. config.py 파일에서 NAVER_API_CONFIG 수정")
        print("2. 또는 환경변수 NAVER_CLIENT_ID, NAVER_CLIENT_SECRET 설정")
        return
    
    # 크롤러 초기화
    crawler = NaverBlogCrawler(client_id, client_secret)
    
    # 검색 실행
    query = "파이썬 머신러닝"
    blog_posts = crawler.crawl_blogs(
        query=query,
        max_results=20,
        include_details=True
    )
    
    # 결과 출력
    print(f"검색 키워드: {query}")
    print(f"검색 결과: {len(blog_posts)}개")
    
    for i, post in enumerate(blog_posts[:5], 1):
        print(f"\n{i}. {post.title}")
        print(f"   블로그: {post.blog_name}")
        print(f"   날짜: {post.post_date}")
        print(f"   댓글: {post.comments_count}개, 좋아요: {post.likes_count}개")
    
    # 결과 저장
    crawler.save_to_csv(blog_posts, "basic_search_result.csv")
    crawler.save_to_json(blog_posts, "basic_search_result.json")

def example_date_filtered_search():
    """날짜 필터링 검색 예시"""
    print("\n=== 날짜 필터링 검색 예시 ===")
    
    client_id = os.getenv("NAVER_CLIENT_ID", NAVER_API_CONFIG["CLIENT_ID"])
    client_secret = os.getenv("NAVER_CLIENT_SECRET", NAVER_API_CONFIG["CLIENT_SECRET"])
    
    if not client_id or not client_secret or client_id == "YOUR_CLIENT_ID_HERE":
        print("네이버 API 키를 설정해주세요!")
        return
    
    crawler = NaverBlogCrawler(client_id, client_secret)
    
    # 최근 30일 검색
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    query = "리액트 개발"
    blog_posts = crawler.crawl_blogs(
        query=query,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        max_results=30,
        include_details=True
    )
    
    print(f"검색 키워드: {query}")
    print(f"검색 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
    print(f"검색 결과: {len(blog_posts)}개")
    
    # 통계 출력
    if blog_posts:
        total_comments = sum(post.comments_count for post in blog_posts)
        total_likes = sum(post.likes_count for post in blog_posts)
        
        print(f"총 댓글 수: {total_comments}개")
        print(f"총 좋아요 수: {total_likes}개")
        print(f"평균 댓글 수: {total_comments / len(blog_posts):.1f}개")
        print(f"평균 좋아요 수: {total_likes / len(blog_posts):.1f}개")
    
    # 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    crawler.save_to_csv(blog_posts, f"date_filtered_search_{timestamp}.csv")

def example_keyword_analysis():
    """키워드 분석 예시"""
    print("\n=== 키워드 분석 예시 ===")
    
    client_id = os.getenv("NAVER_CLIENT_ID", NAVER_API_CONFIG["CLIENT_ID"])
    client_secret = os.getenv("NAVER_CLIENT_SECRET", NAVER_API_CONFIG["CLIENT_SECRET"])
    
    if not client_id or not client_secret or client_id == "YOUR_CLIENT_ID_HERE":
        print("네이버 API 키를 설정해주세요!")
        return
    
    crawler = NaverBlogCrawler(client_id, client_secret)
    
    # 여러 키워드로 검색
    keywords = ["인공지능", "딥러닝", "자연어처리"]
    all_results = {}
    
    for keyword in keywords:
        print(f"'{keyword}' 검색 중...")
        blog_posts = crawler.crawl_blogs(
            query=keyword,
            max_results=20,
            include_details=True
        )
        all_results[keyword] = blog_posts
        
        print(f"  - 검색 결과: {len(blog_posts)}개")
        if blog_posts:
            avg_comments = sum(post.comments_count for post in blog_posts) / len(blog_posts)
            avg_likes = sum(post.likes_count for post in blog_posts) / len(blog_posts)
            print(f"  - 평균 댓글: {avg_comments:.1f}개, 평균 좋아요: {avg_likes:.1f}개")
    
    # 키워드별 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for keyword, posts in all_results.items():
        filename = f"keyword_analysis_{keyword}_{timestamp}.csv"
        crawler.save_to_csv(posts, filename)

def example_comment_analysis():
    """댓글 분석 예시"""
    print("\n=== 댓글 분석 예시 ===")
    
    client_id = os.getenv("NAVER_CLIENT_ID", NAVER_API_CONFIG["CLIENT_ID"])
    client_secret = os.getenv("NAVER_CLIENT_SECRET", NAVER_API_CONFIG["CLIENT_SECRET"])
    
    if not client_id or not client_secret or client_id == "YOUR_CLIENT_ID_HERE":
        print("네이버 API 키를 설정해주세요!")
        return
    
    crawler = NaverBlogCrawler(client_id, client_secret)
    
    query = "프로그래밍 공부법"
    blog_posts = crawler.crawl_blogs(
        query=query,
        max_results=15,
        include_details=True
    )
    
    print(f"검색 키워드: {query}")
    print(f"검색 결과: {len(blog_posts)}개")
    
    # 댓글이 많은 게시글 분석
    posts_with_comments = [post for post in blog_posts if post.comments_count > 0]
    posts_with_comments.sort(key=lambda x: x.comments_count, reverse=True)
    
    print(f"\n댓글이 있는 게시글: {len(posts_with_comments)}개")
    
    if posts_with_comments:
        print("\n=== 댓글이 많은 게시글 TOP 5 ===")
        for i, post in enumerate(posts_with_comments[:5], 1):
            print(f"{i}. {post.title[:50]}...")
            print(f"   댓글: {post.comments_count}개, 좋아요: {post.likes_count}개")
            
            # 댓글 미리보기
            if post.comments:
                print(f"   댓글 미리보기:")
                for j, comment in enumerate(post.comments[:3], 1):
                    comment_preview = comment['text'][:100] + "..." if len(comment['text']) > 100 else comment['text']
                    print(f"     {j}) {comment_preview}")
            print()

def main():
    """메인 실행 함수"""
    print("네이버 블로그 크롤러 사용 예시")
    print("=" * 50)
    
    # 출력 디렉토리 생성
    output_dir = OUTPUT_CONFIG["OUTPUT_DIR"]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"출력 디렉토리 생성: {output_dir}")
    
    try:
        # 각 예시 실행
        example_basic_search()
        example_date_filtered_search()
        example_keyword_analysis()
        example_comment_analysis()
        
    except Exception as e:
        print(f"실행 중 오류 발생: {e}")
        print("API 키가 올바르게 설정되었는지 확인해주세요.")

if __name__ == "__main__":
    main()