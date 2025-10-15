"""
YouTube API를 사용한 동영상 및 댓글 크롤러
키워드 검색을 통해 동영상 정보와 댓글을 수집합니다.
"""

import os
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import time

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("Google API 클라이언트가 설치되지 않았습니다.")
    print("pip install google-api-python-client를 실행해주세요.")
    exit(1)


class YouTubeCrawler:
    """YouTube API를 사용한 크롤러 클래스"""
    
    def __init__(self, api_key: str):
        """
        YouTube API 클라이언트 초기화
        
        Args:
            api_key (str): YouTube Data API v3 키
        """
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.results = []
        
    def search_videos(self, 
                     keyword: str, 
                     max_results: int = 50,
                     published_after: Optional[str] = None,
                     published_before: Optional[str] = None,
                     order: str = 'relevance') -> List[Dict]:
        """
        키워드로 동영상 검색
        
        Args:
            keyword (str): 검색 키워드
            max_results (int): 최대 결과 수 (기본값: 50)
            published_after (str): 시작 날짜 (ISO 8601 형식, 예: '2023-01-01T00:00:00Z')
            published_before (str): 종료 날짜 (ISO 8601 형식)
            order (str): 정렬 순서 ('relevance', 'date', 'rating', 'viewCount', 'title')
            
        Returns:
            List[Dict]: 검색된 동영상 정보 리스트
        """
        try:
            print(f"키워드 '{keyword}'로 동영상 검색 중...")
            
            search_params = {
                'part': 'id,snippet',
                'q': keyword,
                'type': 'video',
                'maxResults': min(max_results, 50),  # API 제한으로 한 번에 최대 50개
                'order': order
            }
            
            if published_after:
                search_params['publishedAfter'] = published_after
            if published_before:
                search_params['publishedBefore'] = published_before
                
            videos = []
            next_page_token = None
            collected = 0
            
            while collected < max_results:
                if next_page_token:
                    search_params['pageToken'] = next_page_token
                    
                search_response = self.youtube.search().list(**search_params).execute()
                
                for item in search_response['items']:
                    if collected >= max_results:
                        break
                        
                    video_info = {
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'channel_title': item['snippet']['channelTitle'],
                        'channel_id': item['snippet']['channelId'],
                        'published_at': item['snippet']['publishedAt'],
                        'thumbnail_url': item['snippet']['thumbnails'].get('high', {}).get('url', '')
                    }
                    videos.append(video_info)
                    collected += 1
                    
                next_page_token = search_response.get('nextPageToken')
                if not next_page_token:
                    break
                    
                # API 호출 제한을 위한 대기
                time.sleep(0.1)
                
            print(f"총 {len(videos)}개의 동영상을 찾았습니다.")
            return videos
            
        except HttpError as e:
            print(f"YouTube API 오류: {e}")
            return []
        except Exception as e:
            print(f"검색 중 오류 발생: {e}")
            return []
    
    def get_video_details(self, video_ids: List[str]) -> List[Dict]:
        """
        동영상 상세 정보 가져오기 (조회수, 좋아요 수 등)
        
        Args:
            video_ids (List[str]): 동영상 ID 리스트
            
        Returns:
            List[Dict]: 동영상 상세 정보 리스트
        """
        try:
            print(f"{len(video_ids)}개 동영상의 상세 정보를 가져오는 중...")
            
            video_details = []
            
            # API 제한으로 인해 50개씩 나누어서 요청
            for i in range(0, len(video_ids), 50):
                batch_ids = video_ids[i:i+50]
                
                videos_response = self.youtube.videos().list(
                    part='statistics,contentDetails,snippet',
                    id=','.join(batch_ids)
                ).execute()
                
                for item in videos_response['items']:
                    stats = item.get('statistics', {})
                    content_details = item.get('contentDetails', {})
                    snippet = item.get('snippet', {})
                    
                    detail_info = {
                        'video_id': item['id'],
                        'view_count': int(stats.get('viewCount', 0)),
                        'like_count': int(stats.get('likeCount', 0)),
                        'comment_count': int(stats.get('commentCount', 0)),
                        'duration': content_details.get('duration', ''),
                        'definition': content_details.get('definition', ''),
                        'category_id': snippet.get('categoryId', ''),
                        'tags': snippet.get('tags', [])
                    }
                    video_details.append(detail_info)
                    
                # API 호출 제한을 위한 대기
                time.sleep(0.1)
                
            print(f"{len(video_details)}개 동영상의 상세 정보를 수집했습니다.")
            return video_details
            
        except HttpError as e:
            print(f"YouTube API 오류: {e}")
            return []
        except Exception as e:
            print(f"동영상 정보 수집 중 오류 발생: {e}")
            return []
    
    def get_video_comments(self, video_id: str, max_comments: int = 100) -> List[Dict]:
        """
        동영상의 댓글 가져오기
        
        Args:
            video_id (str): 동영상 ID
            max_comments (int): 최대 댓글 수 (기본값: 100)
            
        Returns:
            List[Dict]: 댓글 정보 리스트
        """
        try:
            print(f"동영상 {video_id}의 댓글을 수집하는 중...")
            
            comments = []
            next_page_token = None
            collected = 0
            
            while collected < max_comments:
                try:
                    comment_params = {
                        'part': 'snippet,replies',
                        'videoId': video_id,
                        'maxResults': min(100, max_comments - collected),
                        'order': 'relevance'
                    }
                    
                    if next_page_token:
                        comment_params['pageToken'] = next_page_token
                    
                    comments_response = self.youtube.commentThreads().list(**comment_params).execute()
                    
                    for item in comments_response['items']:
                        if collected >= max_comments:
                            break
                            
                        top_comment = item['snippet']['topLevelComment']['snippet']
                        
                        comment_info = {
                            'comment_id': item['snippet']['topLevelComment']['id'],
                            'video_id': video_id,
                            'author_name': top_comment['authorDisplayName'],
                            'author_channel_id': top_comment.get('authorChannelId', {}).get('value', ''),
                            'text': top_comment['textDisplay'],
                            'like_count': top_comment.get('likeCount', 0),
                            'published_at': top_comment['publishedAt'],
                            'updated_at': top_comment.get('updatedAt', ''),
                            'reply_count': item['snippet'].get('totalReplyCount', 0),
                            'is_reply': False
                        }
                        comments.append(comment_info)
                        collected += 1
                        
                        # 대댓글도 수집 (제한적으로)
                        if 'replies' in item and collected < max_comments:
                            for reply in item['replies']['comments'][:5]:  # 대댓글은 최대 5개만
                                if collected >= max_comments:
                                    break
                                    
                                reply_snippet = reply['snippet']
                                reply_info = {
                                    'comment_id': reply['id'],
                                    'video_id': video_id,
                                    'author_name': reply_snippet['authorDisplayName'],
                                    'author_channel_id': reply_snippet.get('authorChannelId', {}).get('value', ''),
                                    'text': reply_snippet['textDisplay'],
                                    'like_count': reply_snippet.get('likeCount', 0),
                                    'published_at': reply_snippet['publishedAt'],
                                    'updated_at': reply_snippet.get('updatedAt', ''),
                                    'reply_count': 0,
                                    'is_reply': True,
                                    'parent_comment_id': item['snippet']['topLevelComment']['id']
                                }
                                comments.append(reply_info)
                                collected += 1
                    
                    next_page_token = comments_response.get('nextPageToken')
                    if not next_page_token:
                        break
                        
                    # API 호출 제한을 위한 대기
                    time.sleep(0.1)
                    
                except HttpError as e:
                    if e.resp.status == 403:
                        print(f"동영상 {video_id}의 댓글이 비활성화되어 있습니다.")
                        break
                    else:
                        print(f"댓글 수집 중 API 오류: {e}")
                        break
                        
            print(f"동영상 {video_id}에서 {len(comments)}개의 댓글을 수집했습니다.")
            return comments
            
        except Exception as e:
            print(f"댓글 수집 중 오류 발생: {e}")
            return []
    
    def crawl_keyword(self, 
                     keyword: str,
                     max_videos: int = 50,
                     max_comments_per_video: int = 100,
                     days_back: int = 30,
                     save_format: str = 'json') -> Dict[str, Any]:
        """
        키워드로 전체 크롤링 실행
        
        Args:
            keyword (str): 검색 키워드
            max_videos (int): 최대 동영상 수
            max_comments_per_video (int): 동영상당 최대 댓글 수
            days_back (int): 몇 일 전까지의 동영상을 검색할지
            save_format (str): 저장 형식 ('json', 'csv')
            
        Returns:
            Dict[str, Any]: 수집된 모든 데이터
        """
        print(f"=== YouTube 크롤링 시작: '{keyword}' ===")
        print(f"설정: 최대 {max_videos}개 동영상, 동영상당 최대 {max_comments_per_video}개 댓글")
        print(f"기간: 최근 {days_back}일")
        
        # 날짜 범위 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        published_after = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        published_before = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # 1. 동영상 검색
        videos = self.search_videos(
            keyword=keyword,
            max_results=max_videos,
            published_after=published_after,
            published_before=published_before
        )
        
        if not videos:
            print("검색된 동영상이 없습니다.")
            return {'videos': [], 'comments': []}
        
        # 2. 동영상 상세 정보 수집
        video_ids = [video['video_id'] for video in videos]
        video_details = self.get_video_details(video_ids)
        
        # 동영상 정보와 상세 정보 병합
        video_details_dict = {detail['video_id']: detail for detail in video_details}
        
        for video in videos:
            video_id = video['video_id']
            if video_id in video_details_dict:
                video.update(video_details_dict[video_id])
        
        # 3. 댓글 수집
        all_comments = []
        for i, video in enumerate(videos, 1):
            print(f"\n진행률: {i}/{len(videos)} - {video['title'][:50]}...")
            
            comments = self.get_video_comments(
                video_id=video['video_id'],
                max_comments=max_comments_per_video
            )
            all_comments.extend(comments)
            
            # API 제한을 위한 대기
            time.sleep(0.5)
        
        # 4. 결과 정리
        result_data = {
            'keyword': keyword,
            'crawl_date': datetime.now().isoformat(),
            'total_videos': len(videos),
            'total_comments': len(all_comments),
            'videos': videos,
            'comments': all_comments
        }
        
        # 5. 데이터 저장
        self.save_data(result_data, keyword, save_format)
        
        print(f"\n=== 크롤링 완료 ===")
        print(f"수집된 동영상: {len(videos)}개")
        print(f"수집된 댓글: {len(all_comments)}개")
        
        return result_data
    
    def save_data(self, data: Dict[str, Any], keyword: str, format_type: str = 'json'):
        """
        수집된 데이터를 파일로 저장
        
        Args:
            data (Dict[str, Any]): 저장할 데이터
            keyword (str): 검색 키워드 (파일명에 사용)
            format_type (str): 저장 형식 ('json', 'csv')
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_keyword = "".join(c for c in keyword if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        if format_type.lower() == 'json':
            filename = f"youtube_data_{safe_keyword}_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"JSON 파일로 저장됨: {filename}")
            
        elif format_type.lower() == 'csv':
            # 동영상 데이터 CSV 저장
            videos_filename = f"youtube_videos_{safe_keyword}_{timestamp}.csv"
            if data['videos']:
                with open(videos_filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=data['videos'][0].keys())
                    writer.writeheader()
                    writer.writerows(data['videos'])
                print(f"동영상 CSV 파일로 저장됨: {videos_filename}")
            
            # 댓글 데이터 CSV 저장
            comments_filename = f"youtube_comments_{safe_keyword}_{timestamp}.csv"
            if data['comments']:
                with open(comments_filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=data['comments'][0].keys())
                    writer.writeheader()
                    writer.writerows(data['comments'])
                print(f"댓글 CSV 파일로 저장됨: {comments_filename}")


def main():
    """메인 실행 함수"""
    print("YouTube API 크롤러")
    print("=" * 50)
    
    # API 키 입력
    api_key = input("YouTube Data API v3 키를 입력하세요: ").strip()
    if not api_key:
        print("API 키가 필요합니다.")
        return
    
    # 크롤러 초기화
    crawler = YouTubeCrawler(api_key)
    
    # 검색 설정
    keyword = input("검색할 키워드를 입력하세요: ").strip()
    if not keyword:
        print("키워드가 필요합니다.")
        return
    
    try:
        max_videos = int(input("최대 동영상 수 (기본값: 50): ") or "50")
        max_comments = int(input("동영상당 최대 댓글 수 (기본값: 100): ") or "100")
        days_back = int(input("몇 일 전까지 검색할지 (기본값: 30): ") or "30")
    except ValueError:
        print("숫자를 입력해주세요. 기본값을 사용합니다.")
        max_videos, max_comments, days_back = 50, 100, 30
    
    save_format = input("저장 형식 (json/csv, 기본값: json): ").strip().lower() or "json"
    
    # 크롤링 실행
    try:
        result = crawler.crawl_keyword(
            keyword=keyword,
            max_videos=max_videos,
            max_comments_per_video=max_comments,
            days_back=days_back,
            save_format=save_format
        )
        
        print("\n크롤링이 성공적으로 완료되었습니다!")
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main()