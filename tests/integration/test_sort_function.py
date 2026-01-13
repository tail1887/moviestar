"""
통합 테스트: 정렬 기능
- GET /api/list의 sortMode 파라미터 테스트
- likes, viewers, date 순 정렬 검증
"""
import unittest
import sys
import os

# 프로젝트 루트 디렉토리를 Python path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import app, db


class TestSortFunction(unittest.TestCase):
    """정렬 기능 통합 테스트"""

    @classmethod
    def setUpClass(cls):
        """테스트 클래스 시작 전 한 번 실행"""
        app.config['TESTING'] = True
        cls.client = app.test_client()

    def setUp(self):
        """각 테스트 전 실행 - 테스트용 영화 데이터 추가"""
        # 테스트용 영화 3개 삽입 (정렬 테스트용)
        self.test_movies = [
            {
                'title': '테스트영화A_정렬용',
                'poster_url': 'https://test.com/a.jpg',
                'info_url': 'https://test.com/a',
                'open_year': 2024,
                'open_month': 12,
                'open_day': 25,
                'viewers': 1000000,
                'likes': 10,
                'trashed': False
            },
            {
                'title': '테스트영화B_정렬용',
                'poster_url': 'https://test.com/b.jpg',
                'info_url': 'https://test.com/b',
                'open_year': 2024,
                'open_month': 6,
                'open_day': 15,
                'viewers': 5000000,
                'likes': 50,
                'trashed': False
            },
            {
                'title': '테스트영화C_정렬용',
                'poster_url': 'https://test.com/c.jpg',
                'info_url': 'https://test.com/c',
                'open_year': 2023,
                'open_month': 3,
                'open_day': 10,
                'viewers': 3000000,
                'likes': 30,
                'trashed': False
            }
        ]
        db.movies.insert_many(self.test_movies)

    def tearDown(self):
        """각 테스트 후 실행 - 테스트 데이터 삭제"""
        db.movies.delete_many({'title': {'$regex': '테스트영화.*_정렬용'}})

    def test_sort_by_likes(self):
        """좋아요 순 정렬 테스트"""
        response = self.client.get('/api/list?sortMode=likes')
        data = response.get_json()
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['result'], 'success')
        
        # 테스트 영화만 필터링
        test_movies = [m for m in data['movies_list'] if '정렬용' in m['title']]
        
        # 좋아요 순으로 정렬되었는지 확인 (50 > 30 > 10)
        self.assertEqual(test_movies[0]['title'], '테스트영화B_정렬용')
        self.assertEqual(test_movies[1]['title'], '테스트영화C_정렬용')
        self.assertEqual(test_movies[2]['title'], '테스트영화A_정렬용')

    def test_sort_by_viewers(self):
        """관객수 순 정렬 테스트"""
        response = self.client.get('/api/list?sortMode=viewers')
        data = response.get_json()
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['result'], 'success')
        
        # 테스트 영화만 필터링
        test_movies = [m for m in data['movies_list'] if '정렬용' in m['title']]
        
        # 관객수 순으로 정렬되었는지 확인 (5M > 3M > 1M)
        self.assertEqual(test_movies[0]['title'], '테스트영화B_정렬용')
        self.assertEqual(test_movies[1]['title'], '테스트영화C_정렬용')
        self.assertEqual(test_movies[2]['title'], '테스트영화A_정렬용')

    def test_sort_by_date(self):
        """개봉일 순 정렬 테스트"""
        response = self.client.get('/api/list?sortMode=date')
        data = response.get_json()
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['result'], 'success')
        
        # 테스트 영화만 필터링
        test_movies = [m for m in data['movies_list'] if '정렬용' in m['title']]
        
        # 최신 개봉일 순으로 정렬되었는지 확인
        # 2024-12-25 > 2024-06-15 > 2023-03-10
        self.assertEqual(test_movies[0]['title'], '테스트영화A_정렬용')
        self.assertEqual(test_movies[1]['title'], '테스트영화B_정렬용')
        self.assertEqual(test_movies[2]['title'], '테스트영화C_정렬용')

    def test_sort_default_is_likes(self):
        """정렬 모드를 지정하지 않으면 기본값(likes)으로 정렬되는지 테스트"""
        response = self.client.get('/api/list')
        data = response.get_json()
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['result'], 'success')
        
        # 테스트 영화만 필터링
        test_movies = [m for m in data['movies_list'] if '정렬용' in m['title']]
        
        # 좋아요 순(기본값)으로 정렬되었는지 확인
        self.assertEqual(test_movies[0]['likes'], 50)

    def test_sort_invalid_mode(self):
        """지원하지 않는 정렬 모드 테스트"""
        response = self.client.get('/api/list?sortMode=invalid')
        data = response.get_json()
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['result'], 'failure')
        self.assertIn('지원하지 않는', data['msg'])


if __name__ == '__main__':
    unittest.main()
