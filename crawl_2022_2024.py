"""
2022년부터 2024년까지의 YouTube 데이터 크롤링 전용 스크립트
"""

import sys
from datetime import datetime
from youtube_crawler import YouTubeCrawler

# config.py 파일이 있는지 확인
try:
    from config import YOUTUBE_API_KEY
except ImportError:
    print("config.py 파일이 없습니다.")
    print("config_example.py를 config.py로 복사하고 API 키를 설정해주세요.")
    YOUTUBE_API_KEY = None


def crawl_2022_2024(keywords_list, api_key=None, max_videos=100, max_comments=150):
    """
    2022년부터 2024년까지의 데이터를 크롤링
    
    Args:
        keywords_list (list): 크롤링할 키워드 리스트
        api_key (str): API 키
        max_videos (int): 키워드당 최대 동영상 수
        max_comments (int): 동영상당 최대 댓글 수
    """
    if not api_key:
        api_key = YOUTUBE_API_KEY
    
    if not api_key or api_key == "YOUR_YOUTUBE_API_KEY_HERE":
        print("API 키가 설정되지 않았습니다.")
        api_key = input("YouTube Data API v3 키를 입력하세요: ").strip()
        if not api_key:
            print("API 키가 필요합니다.")
            return
    
    crawler = YouTubeCrawler(api_key)
    
    # 2022년 1월 1일부터 2024년 12월 31일까지
    start_date = "2022-01-01"
    end_date = "2024-12-31"
    
    print("🎯 2022-2024년 YouTube 데이터 크롤링")
    print("=" * 60)
    print(f"📅 검색 기간: {start_date} ~ {end_date}")
    print(f"🔍 키워드 수: {len(keywords_list)}개")
    print(f"📊 키워드당 최대 동영상: {max_videos}개")
    print(f"💬 동영상당 최대 댓글: {max_comments}개")
    print("=" * 60)
    
    results = {}
    total_videos = 0
    total_comments = 0
    
    for i, keyword in enumerate(keywords_list, 1):
        print(f"\n[{i}/{len(keywords_list)}] 🔍 키워드: '{keyword}' 크롤링 시작")
        
        try:
            result = crawler.crawl_keyword(
                keyword=keyword,
                max_videos=max_videos,
                max_comments_per_video=max_comments,
                start_date=start_date,
                end_date=end_date,
                save_format="json"  # JSON으로 저장
            )
            
            videos_count = len(result['videos'])
            comments_count = len(result['comments'])
            
            results[keyword] = {
                'success': True,
                'videos_count': videos_count,
                'comments_count': comments_count,
                'period': f"{start_date} ~ {end_date}"
            }
            
            total_videos += videos_count
            total_comments += comments_count
            
            print(f"✅ '{keyword}' 완료: 동영상 {videos_count}개, 댓글 {comments_count}개")
            
        except Exception as e:
            print(f"❌ '{keyword}' 실패: {e}")
            results[keyword] = {
                'success': False,
                'error': str(e)
            }
    
    # 최종 결과 요약
    print("\n" + "🎉 크롤링 완료!" + "=" * 50)
    print(f"⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 검색 기간: {start_date} ~ {end_date}")
    
    success_count = sum(1 for r in results.values() if r['success'])
    
    print(f"\n📊 전체 결과:")
    print(f"   ✅ 성공한 키워드: {success_count}/{len(keywords_list)}개")
    print(f"   📺 총 수집 동영상: {total_videos:,}개")
    print(f"   💬 총 수집 댓글: {total_comments:,}개")
    
    print(f"\n📋 키워드별 상세 결과:")
    for keyword, result in results.items():
        if result['success']:
            print(f"   ✅ {keyword}: 동영상 {result['videos_count']:,}개, 댓글 {result['comments_count']:,}개")
        else:
            print(f"   ❌ {keyword}: {result['error']}")
    
    print(f"\n💾 저장된 파일들:")
    print(f"   각 키워드별로 'youtube_data_[키워드]_[타임스탬프].json' 형식으로 저장됨")
    
    return results


def main():
    """메인 실행 함수"""
    print("🎯 2022-2024년 YouTube 크롤러")
    print("=" * 50)
    
    # 키워드 입력 방식 선택
    print("키워드 입력 방식을 선택하세요:")
    print("1. 직접 입력 (쉼표로 구분)")
    print("2. 파일에서 읽기 (keywords_2022_2024.txt)")
    
    choice = input("선택 (1 또는 2): ").strip()
    
    keywords = []
    
    if choice == "1":
        keyword_input = input("키워드들을 쉼표로 구분하여 입력하세요: ").strip()
        keywords = [k.strip() for k in keyword_input.split(',') if k.strip()]
        
    elif choice == "2":
        filename = "keywords_2022_2024.txt"
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                keywords = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        except FileNotFoundError:
            print(f"{filename} 파일이 없습니다.")
            print("파일을 생성하고 각 줄에 하나씩 키워드를 입력해주세요.")
            
            # 기본 키워드 파일 생성
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("""# 2022-2024년 크롤링할 키워드를 한 줄에 하나씩 입력하세요
# 예시:
# 파이썬 프로그래밍
# 머신러닝
# 웹개발
# 데이터 분석
# 인공지능
""")
            print(f"{filename} 파일이 생성되었습니다. 키워드를 입력하고 다시 실행해주세요.")
            return
    else:
        print("잘못된 선택입니다.")
        return
    
    if not keywords:
        print("키워드가 없습니다.")
        return
    
    # 크롤링 설정
    print(f"\n🔍 크롤링할 키워드 ({len(keywords)}개):")
    for i, keyword in enumerate(keywords, 1):
        print(f"   {i}. {keyword}")
    
    try:
        max_videos = int(input(f"\n키워드당 최대 동영상 수 (기본값: 100, 권장: 50-200): ") or "100")
        max_comments = int(input(f"동영상당 최대 댓글 수 (기본값: 150, 권장: 100-300): ") or "150")
    except ValueError:
        print("숫자를 입력해주세요. 기본값을 사용합니다.")
        max_videos, max_comments = 100, 150
    
    print(f"\n⚠️  주의사항:")
    print(f"   - 총 예상 API 호출량: 약 {len(keywords) * (max_videos // 50 + 1 + max_videos * 2):,}회")
    print(f"   - 2022-2024년은 3년간의 데이터로 양이 많을 수 있습니다")
    print(f"   - 크롤링 시간: 약 {len(keywords) * max_videos * 0.5 / 60:.1f}분 예상")
    
    confirm = input(f"\n2022-2024년 데이터 크롤링을 시작하시겠습니까? (y/n): ").strip().lower()
    
    if confirm == 'y':
        crawl_2022_2024(keywords, max_videos=max_videos, max_comments=max_comments)
    else:
        print("취소되었습니다.")


if __name__ == "__main__":
    main()