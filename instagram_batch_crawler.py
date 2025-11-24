"""
Instagram 배치 크롤링 시스템

여러 키워드를 한 번에 크롤링하고 결과를 통합하여 저장하는 시스템입니다.
"""

import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from instagram_crawler import InstagramCrawler


class InstagramBatchCrawler:
    """인스타그램 배치 크롤링 클래스"""
    
    def __init__(self, username: str = None, password: str = None, max_workers: int = 3):
        """
        배치 크롤러 초기화
        
        Args:
            username: 인스타그램 사용자명
            password: 인스타그램 비밀번호
            max_workers: 동시 실행할 최대 크롤러 수
        """
        self.username = username
        self.password = password
        self.max_workers = max_workers
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def crawl_keywords_from_list(self, keywords: List[str], max_posts: int = 50, 
                                max_comments_per_post: int = 100, days_back: int = 30,
                                save_format: str = "json", parallel: bool = False) -> Dict[str, Any]:
        """
        키워드 리스트로 배치 크롤링
        
        Args:
            keywords: 크롤링할 키워드 리스트
            max_posts: 키워드당 최대 게시글 수
            max_comments_per_post: 게시글당 최대 댓글 수
            days_back: 검색 기간 (일)
            save_format: 저장 형식 ("json" 또는 "csv")
            parallel: 병렬 처리 여부
            
        Returns:
            통합된 크롤링 결과
        """
        self.logger.info(f"Starting batch crawl for {len(keywords)} keywords")
        
        all_results = {}
        failed_keywords = []
        
        if parallel and len(keywords) > 1:
            # 병렬 처리
            all_results = self._crawl_parallel(
                keywords, max_posts, max_comments_per_post, days_back, save_format
            )
        else:
            # 순차 처리
            for i, keyword in enumerate(keywords):
                self.logger.info(f"Processing keyword {i+1}/{len(keywords)}: {keyword}")
                
                try:
                    crawler = InstagramCrawler(self.username, self.password)
                    result = crawler.crawl_keyword(
                        keyword=keyword,
                        max_posts=max_posts,
                        max_comments_per_post=max_comments_per_post,
                        days_back=days_back,
                        save_format=save_format
                    )
                    all_results[keyword] = result
                    
                    # 키워드 간 간격
                    if i < len(keywords) - 1:
                        time.sleep(5)
                        
                except Exception as e:
                    self.logger.error(f"Failed to crawl keyword '{keyword}': {e}")
                    failed_keywords.append(keyword)
        
        # 통합 결과 생성
        summary_result = self._create_batch_summary(all_results, failed_keywords)
        
        # 통합 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_filename = f"instagram_batch_summary_{timestamp}.json"
        
        with open(summary_filename, 'w', encoding='utf-8') as f:
            json.dump(summary_result, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Batch crawling completed. Summary saved to {summary_filename}")
        
        return summary_result
    
    def _crawl_parallel(self, keywords: List[str], max_posts: int, max_comments_per_post: int,
                       days_back: int, save_format: str) -> Dict[str, Any]:
        """병렬 크롤링 실행"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 각 키워드에 대한 크롤링 작업 제출
            future_to_keyword = {}
            
            for keyword in keywords:
                future = executor.submit(
                    self._crawl_single_keyword,
                    keyword, max_posts, max_comments_per_post, days_back, save_format
                )
                future_to_keyword[future] = keyword
            
            # 완료된 작업 처리
            for future in as_completed(future_to_keyword):
                keyword = future_to_keyword[future]
                try:
                    result = future.result()
                    results[keyword] = result
                    self.logger.info(f"Completed crawling for keyword: {keyword}")
                except Exception as e:
                    self.logger.error(f"Failed to crawl keyword '{keyword}': {e}")
        
        return results
    
    def _crawl_single_keyword(self, keyword: str, max_posts: int, max_comments_per_post: int,
                             days_back: int, save_format: str) -> Dict[str, Any]:
        """단일 키워드 크롤링 (병렬 처리용)"""
        crawler = InstagramCrawler(self.username, self.password)
        return crawler.crawl_keyword(
            keyword=keyword,
            max_posts=max_posts,
            max_comments_per_post=max_comments_per_post,
            days_back=days_back,
            save_format=save_format
        )
    
    def crawl_keywords_from_file(self, filename: str = "instagram_keywords.txt", 
                                max_posts: int = 50, max_comments_per_post: int = 100,
                                days_back: int = 30, save_format: str = "json",
                                parallel: bool = False) -> Dict[str, Any]:
        """
        파일에서 키워드를 읽어 배치 크롤링
        
        Args:
            filename: 키워드가 저장된 파일명
            max_posts: 키워드당 최대 게시글 수
            max_comments_per_post: 게시글당 최대 댓글 수
            days_back: 검색 기간 (일)
            save_format: 저장 형식
            parallel: 병렬 처리 여부
            
        Returns:
            통합된 크롤링 결과
        """
        if not os.path.exists(filename):
            self.logger.error(f"Keywords file not found: {filename}")
            return {}
        
        # 파일에서 키워드 읽기
        keywords = []
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                keyword = line.strip()
                if keyword and not keyword.startswith('#'):
                    keywords.append(keyword)
        
        if not keywords:
            self.logger.error("No keywords found in file")
            return {}
        
        self.logger.info(f"Loaded {len(keywords)} keywords from {filename}")
        
        return self.crawl_keywords_from_list(
            keywords, max_posts, max_comments_per_post, days_back, save_format, parallel
        )
    
    def _create_batch_summary(self, results: Dict[str, Any], failed_keywords: List[str]) -> Dict[str, Any]:
        """배치 크롤링 결과 요약 생성"""
        total_posts = 0
        total_comments = 0
        total_likes = 0
        successful_keywords = []
        
        for keyword, result in results.items():
            if result and 'summary' in result:
                total_posts += result['summary']['total_posts']
                total_comments += result['summary']['total_comments']
                total_likes += result['summary']['total_likes']
                successful_keywords.append(keyword)
        
        return {
            'batch_crawl_date': datetime.now().isoformat(),
            'total_keywords': len(results) + len(failed_keywords),
            'successful_keywords': successful_keywords,
            'failed_keywords': failed_keywords,
            'overall_summary': {
                'total_posts': total_posts,
                'total_comments': total_comments,
                'total_likes': total_likes,
                'success_rate': len(successful_keywords) / (len(results) + len(failed_keywords)) * 100
            },
            'keyword_results': results
        }
    
    def create_combined_dataset(self, results: Dict[str, Any], output_filename: str = None) -> str:
        """
        모든 키워드의 결과를 하나의 데이터셋으로 통합
        
        Args:
            results: 배치 크롤링 결과
            output_filename: 출력 파일명 (None이면 자동 생성)
            
        Returns:
            생성된 파일명
        """
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"instagram_combined_dataset_{timestamp}.json"
        
        combined_posts = []
        combined_comments = []
        
        for keyword, result in results.get('keyword_results', {}).items():
            if result and 'posts' in result and 'comments' in result:
                # 키워드 정보 추가
                for post in result['posts']:
                    post['search_keyword'] = keyword
                    combined_posts.append(post)
                
                for comment in result['comments']:
                    comment['search_keyword'] = keyword
                    combined_comments.append(comment)
        
        combined_data = {
            'creation_date': datetime.now().isoformat(),
            'total_keywords': len(results.get('successful_keywords', [])),
            'keywords': results.get('successful_keywords', []),
            'posts': combined_posts,
            'comments': combined_comments,
            'summary': {
                'total_posts': len(combined_posts),
                'total_comments': len(combined_comments),
                'posts_per_keyword': len(combined_posts) / max(1, len(results.get('successful_keywords', []))),
                'comments_per_keyword': len(combined_comments) / max(1, len(results.get('successful_keywords', [])))
            }
        }
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Combined dataset saved to {output_filename}")
        return output_filename


def main():
    """대화형 배치 크롤링 실행"""
    print("=== Instagram 배치 키워드 크롤러 ===")
    print()
    
    # 키워드 입력 방식 선택
    print("키워드 입력 방식을 선택하세요:")
    print("1. 직접 입력")
    print("2. 파일에서 읽기")
    
    choice = input("선택 (1 또는 2): ").strip()
    
    keywords = []
    
    if choice == "1":
        # 직접 입력
        print("키워드를 입력하세요 (쉼표로 구분, 예: 맛집, 여행, #패션):")
        keywords_input = input().strip()
        if keywords_input:
            keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
    
    elif choice == "2":
        # 파일에서 읽기
        filename = input("키워드 파일명 (기본값: instagram_keywords.txt): ").strip()
        if not filename:
            filename = "instagram_keywords.txt"
        
        # 파일이 없으면 생성
        if not os.path.exists(filename):
            print(f"{filename} 파일이 없습니다. 새로 생성합니다.")
            print("키워드를 한 줄에 하나씩 입력하세요 (빈 줄 입력시 종료):")
            
            keywords_for_file = []
            while True:
                keyword = input().strip()
                if not keyword:
                    break
                keywords_for_file.append(keyword)
            
            if keywords_for_file:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("# Instagram 크롤링 키워드 목록\n")
                    f.write("# 한 줄에 하나씩 입력하세요\n\n")
                    for keyword in keywords_for_file:
                        f.write(f"{keyword}\n")
                print(f"키워드 파일이 생성되었습니다: {filename}")
        
        # 파일에서 키워드 읽기
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    keyword = line.strip()
                    if keyword and not keyword.startswith('#'):
                        keywords.append(keyword)
        except Exception as e:
            print(f"파일 읽기 오류: {e}")
            return
    
    if not keywords:
        print("키워드가 입력되지 않았습니다.")
        return
    
    print(f"\n크롤링할 키워드: {keywords}")
    
    # 크롤링 설정
    try:
        max_posts = int(input("키워드당 최대 게시글 수 (기본값: 30): ") or "30")
        max_comments = int(input("게시글당 최대 댓글 수 (기본값: 50): ") or "50")
        days_back = int(input("검색 기간 (일, 기본값: 30): ") or "30")
    except ValueError:
        print("잘못된 숫자 입력입니다. 기본값을 사용합니다.")
        max_posts, max_comments, days_back = 30, 50, 30
    
    save_format = input("저장 형식 (json/csv, 기본값: json): ").lower() or "json"
    if save_format not in ["json", "csv"]:
        save_format = "json"
    
    parallel = input("병렬 처리를 사용하시겠습니까? (y/n, 기본값: n): ").lower().startswith('y')
    
    # 로그인 정보 (선택사항)
    print("\n로그인 정보 (선택사항, 더 많은 데이터 수집 가능):")
    username = input("Instagram 사용자명 (선택사항): ").strip()
    password = ""
    if username:
        import getpass
        password = getpass.getpass("Instagram 비밀번호: ")
    
    print(f"\n배치 크롤링 시작")
    print(f"키워드: {len(keywords)}개")
    print(f"설정: 게시글 {max_posts}개/키워드, 댓글 {max_comments}개/게시글, 최근 {days_back}일")
    print(f"병렬 처리: {'사용' if parallel else '미사용'}")
    print("=" * 60)
    
    # 배치 크롤링 실행
    batch_crawler = InstagramBatchCrawler(username=username, password=password)
    
    try:
        result = batch_crawler.crawl_keywords_from_list(
            keywords=keywords,
            max_posts=max_posts,
            max_comments_per_post=max_comments,
            days_back=days_back,
            save_format=save_format,
            parallel=parallel
        )
        
        print("\n=== 배치 크롤링 완료 ===")
        print(f"성공한 키워드: {len(result['successful_keywords'])}개")
        print(f"실패한 키워드: {len(result['failed_keywords'])}개")
        print(f"총 게시글: {result['overall_summary']['total_posts']:,}개")
        print(f"총 댓글: {result['overall_summary']['total_comments']:,}개")
        print(f"총 좋아요: {result['overall_summary']['total_likes']:,}개")
        print(f"성공률: {result['overall_summary']['success_rate']:.1f}%")
        
        if result['failed_keywords']:
            print(f"\n실패한 키워드: {', '.join(result['failed_keywords'])}")
        
        # 통합 데이터셋 생성 여부 확인
        if result['successful_keywords']:
            create_combined = input("\n통합 데이터셋을 생성하시겠습니까? (y/n): ").lower().startswith('y')
            if create_combined:
                combined_file = batch_crawler.create_combined_dataset(result)
                print(f"통합 데이터셋 생성 완료: {combined_file}")
        
    except Exception as e:
        print(f"\n배치 크롤링 중 오류 발생: {e}")
        logging.error(f"Batch crawling error: {e}", exc_info=True)


if __name__ == "__main__":
    main()