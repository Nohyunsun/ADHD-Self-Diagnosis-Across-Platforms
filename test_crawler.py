"""
YouTube 크롤러 테스트 스크립트
API 키 없이도 기본 기능을 테스트할 수 있습니다.
"""

import sys
from youtube_crawler import YouTubeCrawler


def test_crawler_initialization():
    """크롤러 초기화 테스트"""
    print("1. 크롤러 초기화 테스트...")
    
    try:
        # 더미 API 키로 초기화 테스트
        crawler = YouTubeCrawler("test_api_key")
        print("✅ 크롤러 초기화 성공")
        return True
    except Exception as e:
        print(f"❌ 크롤러 초기화 실패: {e}")
        return False


def test_with_real_api():
    """실제 API 키로 테스트"""
    print("\n2. 실제 API 테스트...")
    
    api_key = input("테스트용 YouTube API 키를 입력하세요 (엔터로 건너뛰기): ").strip()
    
    if not api_key:
        print("⏭️  API 키가 없어 실제 테스트를 건너뜁니다.")
        return True
    
    try:
        crawler = YouTubeCrawler(api_key)
        
        # 간단한 검색 테스트 (최소한의 결과)
        print("간단한 검색 테스트 실행 중...")
        videos = crawler.search_videos(
            keyword="python",
            max_results=5,
            order='relevance'
        )
        
        if videos:
            print(f"✅ 검색 성공: {len(videos)}개 동영상 발견")
            
            # 첫 번째 동영상의 상세 정보 테스트
            if videos:
                video_id = videos[0]['video_id']
                details = crawler.get_video_details([video_id])
                
                if details:
                    print(f"✅ 동영상 상세 정보 수집 성공")
                    
                    # 댓글 테스트 (최소한으로)
                    comments = crawler.get_video_comments(video_id, max_comments=5)
                    if comments:
                        print(f"✅ 댓글 수집 성공: {len(comments)}개")
                    else:
                        print("⚠️  댓글 수집 실패 (댓글이 비활성화되었을 수 있음)")
                else:
                    print("❌ 동영상 상세 정보 수집 실패")
        else:
            print("❌ 검색 실패")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ API 테스트 실패: {e}")
        return False


def test_data_processing():
    """데이터 처리 기능 테스트"""
    print("\n3. 데이터 처리 기능 테스트...")
    
    try:
        # 더미 데이터로 저장 기능 테스트
        crawler = YouTubeCrawler("test_api_key")
        
        dummy_data = {
            'keyword': 'test',
            'crawl_date': '2023-12-15T10:30:00',
            'total_videos': 2,
            'total_comments': 3,
            'videos': [
                {
                    'video_id': 'test123',
                    'title': 'Test Video 1',
                    'channel_title': 'Test Channel',
                    'view_count': 1000,
                    'like_count': 50,
                    'comment_count': 10
                },
                {
                    'video_id': 'test456',
                    'title': 'Test Video 2',
                    'channel_title': 'Test Channel 2',
                    'view_count': 2000,
                    'like_count': 100,
                    'comment_count': 20
                }
            ],
            'comments': [
                {
                    'comment_id': 'comment1',
                    'video_id': 'test123',
                    'author_name': 'Test User 1',
                    'text': 'Great video!',
                    'like_count': 5
                },
                {
                    'comment_id': 'comment2',
                    'video_id': 'test123',
                    'author_name': 'Test User 2',
                    'text': 'Thanks for sharing',
                    'like_count': 3
                },
                {
                    'comment_id': 'comment3',
                    'video_id': 'test456',
                    'author_name': 'Test User 3',
                    'text': 'Awesome content',
                    'like_count': 8
                }
            ]
        }
        
        # JSON 저장 테스트
        crawler.save_data(dummy_data, "test", "json")
        print("✅ JSON 저장 기능 테스트 성공")
        
        # CSV 저장 테스트
        crawler.save_data(dummy_data, "test", "csv")
        print("✅ CSV 저장 기능 테스트 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터 처리 테스트 실패: {e}")
        return False


def main():
    """메인 테스트 함수"""
    print("YouTube 크롤러 테스트 시작")
    print("=" * 50)
    
    tests = [
        test_crawler_initialization,
        test_data_processing,
        test_with_real_api
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트가 통과했습니다!")
    else:
        print("⚠️  일부 테스트가 실패했습니다.")
    
    print("\n생성된 테스트 파일들을 확인해보세요:")
    print("- youtube_data_test_*.json")
    print("- youtube_videos_test_*.csv")
    print("- youtube_comments_test_*.csv")


if __name__ == "__main__":
    main()