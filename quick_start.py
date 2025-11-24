"""
Instagram 크롤러 빠른 시작 가이드

이 스크립트는 Instagram 크롤러의 기본 사용법을 보여줍니다.
"""

from instagram_crawler import InstagramCrawler
from instagram_batch_crawler import InstagramBatchCrawler


def example_single_keyword():
    """단일 키워드 크롤링 예시"""
    print("=== 단일 키워드 크롤링 예시 ===")
    
    # 크롤러 초기화 (로그인 정보 없이)
    crawler = InstagramCrawler(headless=True)
    
    try:
        # 키워드로 크롤링 실행
        result = crawler.crawl_keyword(
            keyword="#맛집",           # 검색할 키워드/해시태그
            max_posts=10,             # 최대 게시글 수
            max_comments_per_post=20, # 게시글당 최대 댓글 수
            days_back=7,              # 최근 7일간의 게시글
            save_format="json"        # JSON 형식으로 저장
        )
        
        print(f"✅ 크롤링 완료!")
        print(f"📝 수집된 게시글: {result['summary']['total_posts']}개")
        print(f"💬 수집된 댓글: {result['summary']['total_comments']}개")
        print(f"❤️ 총 좋아요: {result['summary']['total_likes']:,}개")
        
    except Exception as e:
        print(f"❌ 크롤링 실패: {e}")


def example_batch_crawling():
    """배치 크롤링 예시"""
    print("\n=== 배치 크롤링 예시 ===")
    
    # 여러 키워드 정의
    keywords = ["#카페", "#여행", "#맛집"]
    
    # 배치 크롤러 초기화
    batch_crawler = InstagramBatchCrawler()
    
    try:
        # 배치 크롤링 실행
        result = batch_crawler.crawl_keywords_from_list(
            keywords=keywords,
            max_posts=5,              # 키워드당 최대 게시글 수
            max_comments_per_post=10, # 게시글당 최대 댓글 수
            days_back=7,              # 최근 7일간의 게시글
            save_format="json",       # JSON 형식으로 저장
            parallel=False            # 순차 처리 (안정성 우선)
        )
        
        print(f"✅ 배치 크롤링 완료!")
        print(f"🎯 성공한 키워드: {len(result['successful_keywords'])}개")
        print(f"❌ 실패한 키워드: {len(result['failed_keywords'])}개")
        print(f"📝 총 게시글: {result['overall_summary']['total_posts']}개")
        print(f"💬 총 댓글: {result['overall_summary']['total_comments']}개")
        print(f"📊 성공률: {result['overall_summary']['success_rate']:.1f}%")
        
        # 통합 데이터셋 생성
        if result['successful_keywords']:
            combined_file = batch_crawler.create_combined_dataset(result)
            print(f"📁 통합 데이터셋: {combined_file}")
        
    except Exception as e:
        print(f"❌ 배치 크롤링 실패: {e}")


def example_with_login():
    """로그인을 사용한 크롤링 예시"""
    print("\n=== 로그인 사용 크롤링 예시 ===")
    print("⚠️ 주의: 실제 계정 정보를 사용하지 마세요!")
    
    # 로그인 정보와 함께 크롤러 초기화
    # 실제 사용시에는 실제 계정 정보를 입력하세요
    crawler = InstagramCrawler(
        username="your_username",  # 실제 사용자명
        password="your_password",  # 실제 비밀번호
        headless=True
    )
    
    print("💡 로그인을 사용하면 더 많은 데이터를 수집할 수 있지만,")
    print("   계정 제재 위험이 있으니 주의하세요.")


def example_custom_settings():
    """커스텀 설정 예시"""
    print("\n=== 커스텀 설정 예시 ===")
    
    # 더 많은 데이터 수집 설정
    crawler = InstagramCrawler(headless=False)  # 브라우저 창 표시
    
    try:
        result = crawler.crawl_keyword(
            keyword="#일상",
            max_posts=30,             # 더 많은 게시글
            max_comments_per_post=50, # 더 많은 댓글
            days_back=14,             # 2주간의 데이터
            save_format="csv",        # CSV 형식으로 저장
            max_retries=5             # 재시도 횟수 증가
        )
        
        print(f"✅ 커스텀 설정 크롤링 완료!")
        print(f"📝 수집된 게시글: {result['summary']['total_posts']}개")
        
    except Exception as e:
        print(f"❌ 커스텀 설정 크롤링 실패: {e}")


def main():
    """메인 함수 - 모든 예시 실행"""
    print("🚀 Instagram 크롤러 빠른 시작 가이드")
    print("=" * 50)
    
    print("이 스크립트는 Instagram 크롤러의 다양한 사용법을 보여줍니다.")
    print("실제 크롤링을 실행하므로 시간이 걸릴 수 있습니다.")
    
    # 사용자 확인
    proceed = input("\n예시를 실행하시겠습니까? (y/n): ").lower().startswith('y')
    if not proceed:
        print("예시 실행을 취소했습니다.")
        return
    
    # 예시 선택
    print("\n실행할 예시를 선택하세요:")
    print("1. 단일 키워드 크롤링")
    print("2. 배치 크롤링")
    print("3. 로그인 사용 예시 (설명만)")
    print("4. 커스텀 설정 예시")
    print("5. 모든 예시 실행")
    
    choice = input("선택 (1-5): ").strip()
    
    if choice == "1":
        example_single_keyword()
    elif choice == "2":
        example_batch_crawling()
    elif choice == "3":
        example_with_login()
    elif choice == "4":
        example_custom_settings()
    elif choice == "5":
        example_single_keyword()
        example_batch_crawling()
        example_with_login()
        example_custom_settings()
    else:
        print("잘못된 선택입니다.")
        return
    
    print("\n🎉 예시 실행 완료!")
    print("\n📚 더 자세한 사용법은 다음 파일들을 참조하세요:")
    print("- README.md: 전체 가이드")
    print("- instagram_crawler.py: 단일 키워드 크롤링")
    print("- instagram_batch_crawler.py: 배치 크롤링")
    print("- test_instagram_crawler.py: 테스트 및 디버깅")


if __name__ == "__main__":
    main()