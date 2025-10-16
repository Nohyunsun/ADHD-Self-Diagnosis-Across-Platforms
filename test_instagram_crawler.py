"""
Instagram 크롤러 테스트 스크립트

크롤러의 기본 기능을 테스트하고 샘플 데이터를 수집합니다.
"""

import json
import time
from datetime import datetime
import logging

from instagram_crawler import InstagramCrawler
from instagram_batch_crawler import InstagramBatchCrawler


def test_single_keyword():
    """단일 키워드 크롤링 테스트"""
    print("=== 단일 키워드 크롤링 테스트 ===")
    
    # 테스트용 키워드 (해시태그)
    test_keyword = "#맛집"
    
    print(f"테스트 키워드: {test_keyword}")
    print("소량의 데이터로 테스트합니다...")
    
    try:
        crawler = InstagramCrawler(headless=True)
        
        result = crawler.crawl_keyword(
            keyword=test_keyword,
            max_posts=5,  # 테스트용으로 적은 수
            max_comments_per_post=10,
            days_back=7,
            save_format="json"
        )
        
        print("\n=== 테스트 결과 ===")
        print(f"수집된 게시글: {result['summary']['total_posts']}개")
        print(f"수집된 댓글: {result['summary']['total_comments']}개")
        print(f"총 좋아요: {result['summary']['total_likes']:,}개")
        
        # 샘플 게시글 정보 출력
        if result['posts']:
            sample_post = result['posts'][0]
            print(f"\n샘플 게시글:")
            print(f"- 사용자: @{sample_post['username']}")
            print(f"- 내용: {sample_post['caption'][:100]}...")
            print(f"- 좋아요: {sample_post['likes_count']:,}개")
            print(f"- 댓글: {sample_post['comments_count']}개")
        
        return True
        
    except Exception as e:
        print(f"테스트 실패: {e}")
        logging.error(f"Single keyword test failed: {e}", exc_info=True)
        return False


def test_batch_crawling():
    """배치 크롤링 테스트"""
    print("\n=== 배치 크롤링 테스트 ===")
    
    # 테스트용 키워드 리스트
    test_keywords = ["#카페", "#여행", "#일상"]
    
    print(f"테스트 키워드: {test_keywords}")
    print("소량의 데이터로 테스트합니다...")
    
    try:
        batch_crawler = InstagramBatchCrawler()
        
        result = batch_crawler.crawl_keywords_from_list(
            keywords=test_keywords,
            max_posts=3,  # 테스트용으로 적은 수
            max_comments_per_post=5,
            days_back=7,
            save_format="json",
            parallel=False  # 테스트에서는 순차 처리
        )
        
        print("\n=== 배치 테스트 결과 ===")
        print(f"성공한 키워드: {len(result['successful_keywords'])}개")
        print(f"실패한 키워드: {len(result['failed_keywords'])}개")
        print(f"총 게시글: {result['overall_summary']['total_posts']}개")
        print(f"총 댓글: {result['overall_summary']['total_comments']}개")
        print(f"성공률: {result['overall_summary']['success_rate']:.1f}%")
        
        if result['successful_keywords']:
            print(f"성공한 키워드: {', '.join(result['successful_keywords'])}")
        
        if result['failed_keywords']:
            print(f"실패한 키워드: {', '.join(result['failed_keywords'])}")
        
        return True
        
    except Exception as e:
        print(f"배치 테스트 실패: {e}")
        logging.error(f"Batch crawling test failed: {e}", exc_info=True)
        return False


def test_data_formats():
    """데이터 형식 테스트"""
    print("\n=== 데이터 형식 테스트 ===")
    
    test_keyword = "#데일리"
    
    try:
        crawler = InstagramCrawler(headless=True)
        
        # JSON 형식 테스트
        print("JSON 형식으로 저장 테스트...")
        json_result = crawler.crawl_keyword(
            keyword=test_keyword,
            max_posts=2,
            max_comments_per_post=5,
            days_back=7,
            save_format="json"
        )
        
        # CSV 형식 테스트
        print("CSV 형식으로 저장 테스트...")
        csv_result = crawler.crawl_keyword(
            keyword=test_keyword + "_csv",
            max_posts=2,
            max_comments_per_post=5,
            days_back=7,
            save_format="csv"
        )
        
        print("데이터 형식 테스트 완료")
        return True
        
    except Exception as e:
        print(f"데이터 형식 테스트 실패: {e}")
        logging.error(f"Data format test failed: {e}", exc_info=True)
        return False


def run_comprehensive_test():
    """종합 테스트 실행"""
    print("Instagram 크롤러 종합 테스트를 시작합니다...")
    print("=" * 50)
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('test_instagram_crawler.log'),
            logging.StreamHandler()
        ]
    )
    
    test_results = []
    
    # 1. 단일 키워드 테스트
    test_results.append(("단일 키워드 크롤링", test_single_keyword()))
    time.sleep(5)  # 테스트 간 간격
    
    # 2. 배치 크롤링 테스트
    test_results.append(("배치 크롤링", test_batch_crawling()))
    time.sleep(5)
    
    # 3. 데이터 형식 테스트
    test_results.append(("데이터 형식", test_data_formats()))
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("=== 테스트 결과 요약 ===")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n전체 테스트: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트가 성공했습니다!")
        print("\n크롤러가 정상적으로 작동합니다.")
        print("이제 실제 크롤링을 시작할 수 있습니다:")
        print("- python instagram_crawler.py (단일 키워드)")
        print("- python instagram_batch_crawler.py (배치 크롤링)")
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")
        print("로그 파일을 확인하여 문제를 해결해주세요.")


def quick_demo():
    """빠른 데모 실행"""
    print("=== Instagram 크롤러 빠른 데모 ===")
    print("주의: 실제 Instagram에 접속하여 데이터를 수집합니다.")
    
    proceed = input("데모를 실행하시겠습니까? (y/n): ").lower().startswith('y')
    if not proceed:
        print("데모를 취소했습니다.")
        return
    
    demo_keyword = input("데모용 키워드를 입력하세요 (예: #맛집): ").strip()
    if not demo_keyword:
        demo_keyword = "#맛집"
    
    print(f"\n'{demo_keyword}' 키워드로 소량의 데이터를 수집합니다...")
    
    try:
        crawler = InstagramCrawler(headless=False)  # 브라우저 창 표시
        
        result = crawler.crawl_keyword(
            keyword=demo_keyword,
            max_posts=3,
            max_comments_per_post=5,
            days_back=7,
            save_format="json"
        )
        
        print("\n=== 데모 결과 ===")
        print(f"키워드: {demo_keyword}")
        print(f"수집된 게시글: {result['summary']['total_posts']}개")
        print(f"수집된 댓글: {result['summary']['total_comments']}개")
        
        # 수집된 파일 정보
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        expected_filename = f"instagram_data_{demo_keyword.replace('#', '').replace(' ', '_')}_{timestamp}.json"
        print(f"데이터 저장 파일: {expected_filename}")
        
    except Exception as e:
        print(f"데모 실행 중 오류: {e}")


def main():
    """메인 함수"""
    print("Instagram 크롤러 테스트 도구")
    print("=" * 30)
    print("1. 종합 테스트 실행")
    print("2. 빠른 데모")
    print("3. 단일 키워드 테스트만")
    print("4. 배치 크롤링 테스트만")
    
    choice = input("\n선택하세요 (1-4): ").strip()
    
    if choice == "1":
        run_comprehensive_test()
    elif choice == "2":
        quick_demo()
    elif choice == "3":
        test_single_keyword()
    elif choice == "4":
        test_batch_crawling()
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()