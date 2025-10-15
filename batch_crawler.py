"""
배치 크롤링 스크립트
설정 파일을 사용하여 자동으로 여러 키워드를 크롤링합니다.
"""

import os
import sys
from datetime import datetime
from youtube_crawler import YouTubeCrawler

# config.py 파일이 있는지 확인
try:
    from config import YOUTUBE_API_KEY, DEFAULT_MAX_VIDEOS, DEFAULT_MAX_COMMENTS_PER_VIDEO, DEFAULT_DAYS_BACK, DEFAULT_SAVE_FORMAT
except ImportError:
    print("config.py 파일이 없습니다.")
    print("config_example.py를 config.py로 복사하고 API 키를 설정해주세요.")
    sys.exit(1)


def batch_crawl(keywords_list, api_key=None):
    """
    여러 키워드를 배치로 크롤링
    
    Args:
        keywords_list (list): 크롤링할 키워드 리스트
        api_key (str): API 키 (없으면 config에서 가져옴)
    """
    if not api_key:
        api_key = YOUTUBE_API_KEY
    
    if not api_key or api_key == "YOUR_YOUTUBE_API_KEY_HERE":
        print("API 키가 설정되지 않았습니다.")
        print("config.py 파일에서 YOUTUBE_API_KEY를 설정해주세요.")
        return
    
    crawler = YouTubeCrawler(api_key)
    
    print(f"배치 크롤링 시작: {len(keywords_list)}개 키워드")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {}
    
    for i, keyword in enumerate(keywords_list, 1):
        print(f"\n[{i}/{len(keywords_list)}] 키워드: '{keyword}' 크롤링 시작")
        
        try:
            result = crawler.crawl_keyword(
                keyword=keyword,
                max_videos=DEFAULT_MAX_VIDEOS,
                max_comments_per_video=DEFAULT_MAX_COMMENTS_PER_VIDEO,
                days_back=DEFAULT_DAYS_BACK,
                save_format=DEFAULT_SAVE_FORMAT
            )
            
            results[keyword] = {
                'success': True,
                'videos_count': len(result['videos']),
                'comments_count': len(result['comments'])
            }
            
            print(f"✅ '{keyword}' 완료: 동영상 {len(result['videos'])}개, 댓글 {len(result['comments'])}개")
            
        except Exception as e:
            print(f"❌ '{keyword}' 실패: {e}")
            results[keyword] = {
                'success': False,
                'error': str(e)
            }
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("배치 크롤링 완료")
    print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n결과 요약:")
    
    success_count = 0
    total_videos = 0
    total_comments = 0
    
    for keyword, result in results.items():
        if result['success']:
            success_count += 1
            total_videos += result['videos_count']
            total_comments += result['comments_count']
            print(f"✅ {keyword}: 동영상 {result['videos_count']}개, 댓글 {result['comments_count']}개")
        else:
            print(f"❌ {keyword}: {result['error']}")
    
    print(f"\n성공: {success_count}/{len(keywords_list)}개 키워드")
    print(f"총 수집: 동영상 {total_videos}개, 댓글 {total_comments}개")


def main():
    """메인 실행 함수"""
    print("YouTube 배치 크롤러")
    print("=" * 50)
    
    # 키워드 입력 방식 선택
    print("키워드 입력 방식을 선택하세요:")
    print("1. 직접 입력 (쉼표로 구분)")
    print("2. 파일에서 읽기 (keywords.txt)")
    
    choice = input("선택 (1 또는 2): ").strip()
    
    keywords = []
    
    if choice == "1":
        keyword_input = input("키워드들을 쉼표로 구분하여 입력하세요: ").strip()
        keywords = [k.strip() for k in keyword_input.split(',') if k.strip()]
        
    elif choice == "2":
        try:
            with open('keywords.txt', 'r', encoding='utf-8') as f:
                keywords = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("keywords.txt 파일이 없습니다.")
            print("파일을 생성하고 각 줄에 하나씩 키워드를 입력해주세요.")
            return
    else:
        print("잘못된 선택입니다.")
        return
    
    if not keywords:
        print("키워드가 없습니다.")
        return
    
    print(f"\n크롤링할 키워드: {keywords}")
    confirm = input("계속하시겠습니까? (y/n): ").strip().lower()
    
    if confirm == 'y':
        batch_crawl(keywords)
    else:
        print("취소되었습니다.")


if __name__ == "__main__":
    main()