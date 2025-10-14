"""
네이버 블로그 크롤러 사용 예제
"""

from naver_blog_crawler import NaverBlogCrawler
from datetime import datetime, timedelta


def example_basic_usage():
    """기본 사용 예제"""
    # API 키 설정 (실제 키로 교체 필요)
    CLIENT_ID = "YOUR_CLIENT_ID_HERE"
    CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"
    
    # 크롤러 초기화
    crawler = NaverBlogCrawler(CLIENT_ID, CLIENT_SECRET)
    
    # 기본 검색
    keyword = "맛집 추천"
    results = crawler.crawl_all_results(
        keyword=keyword,
        max_results=100
    )
    
    # 결과 저장
    crawler.save_to_csv(results, f"{keyword}_블로그_크롤링.csv")
    print(f"'{keyword}' 검색 결과 {len(results)}개 수집 완료")


def example_date_filtered_usage():
    """날짜 필터링 사용 예제"""
    CLIENT_ID = "YOUR_CLIENT_ID_HERE"
    CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"
    
    crawler = NaverBlogCrawler(CLIENT_ID, CLIENT_SECRET)
    
    # 최근 1개월 데이터만 수집
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    keyword = "코로나 백신"
    results = crawler.crawl_all_results(
        keyword=keyword,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        max_results=200
    )
    
    # 결과 분석
    total_comments = sum(item.get('comment_count', 0) for item in results)
    total_sympathy = sum(item.get('sympathy_count', 0) for item in results)
    
    print(f"=== {keyword} 검색 결과 (최근 1개월) ===")
    print(f"총 게시글: {len(results)}개")
    print(f"총 댓글: {total_comments}개")
    print(f"총 공감: {total_sympathy}개")
    
    # JSON과 CSV 모두 저장
    crawler.save_to_json(results, f"{keyword}_최근1개월.json")
    crawler.save_to_csv(results, f"{keyword}_최근1개월.csv")


def example_multiple_keywords():
    """여러 키워드 검색 예제"""
    CLIENT_ID = "YOUR_CLIENT_ID_HERE"
    CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"
    
    crawler = NaverBlogCrawler(CLIENT_ID, CLIENT_SECRET)
    
    keywords = ["부동산 투자", "주식 투자", "코인 투자"]
    all_results = []
    
    for keyword in keywords:
        print(f"\n'{keyword}' 검색 중...")
        results = crawler.crawl_all_results(
            keyword=keyword,
            max_results=50
        )
        
        # 키워드 정보 추가
        for result in results:
            result['search_keyword'] = keyword
        
        all_results.extend(results)
        print(f"'{keyword}' 검색 완료: {len(results)}개")
    
    # 전체 결과 저장
    crawler.save_to_csv(all_results, "투자_관련_블로그_전체.csv")
    print(f"\n전체 {len(all_results)}개 게시글 수집 완료")


def example_detailed_analysis():
    """상세 분석 예제"""
    CLIENT_ID = "YOUR_CLIENT_ID_HERE"
    CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"
    
    crawler = NaverBlogCrawler(CLIENT_ID, CLIENT_SECRET)
    
    keyword = "다이어트 후기"
    results = crawler.crawl_all_results(
        keyword=keyword,
        max_results=100
    )
    
    # 상세 분석
    print(f"=== '{keyword}' 상세 분석 ===")
    
    # 댓글이 많은 게시글 TOP 10
    sorted_by_comments = sorted(results, key=lambda x: x.get('comment_count', 0), reverse=True)
    print("\n댓글이 많은 게시글 TOP 10:")
    for i, post in enumerate(sorted_by_comments[:10], 1):
        print(f"{i}. {post['title'][:50]}... (댓글: {post.get('comment_count', 0)}개)")
    
    # 공감이 많은 게시글 TOP 10
    sorted_by_sympathy = sorted(results, key=lambda x: x.get('sympathy_count', 0), reverse=True)
    print("\n공감이 많은 게시글 TOP 10:")
    for i, post in enumerate(sorted_by_sympathy[:10], 1):
        print(f"{i}. {post['title'][:50]}... (공감: {post.get('sympathy_count', 0)}개)")
    
    # 월별 게시글 수 분석
    monthly_counts = {}
    for post in results:
        postdate = post.get('postdate', '')
        if postdate and len(postdate) >= 6:
            month = postdate[:6]  # YYYYMM
            monthly_counts[month] = monthly_counts.get(month, 0) + 1
    
    print("\n월별 게시글 수:")
    for month in sorted(monthly_counts.keys()):
        print(f"{month[:4]}년 {month[4:]}월: {monthly_counts[month]}개")
    
    # 결과 저장
    crawler.save_to_csv(results, f"{keyword}_상세분석.csv")


if __name__ == "__main__":
    print("네이버 블로그 크롤러 사용 예제")
    print("1. 기본 사용법")
    print("2. 날짜 필터링")
    print("3. 여러 키워드 검색")
    print("4. 상세 분석")
    
    choice = input("\n실행할 예제 번호를 선택하세요 (1-4): ")
    
    if choice == "1":
        example_basic_usage()
    elif choice == "2":
        example_date_filtered_usage()
    elif choice == "3":
        example_multiple_keywords()
    elif choice == "4":
        example_detailed_analysis()
    else:
        print("잘못된 선택입니다.")