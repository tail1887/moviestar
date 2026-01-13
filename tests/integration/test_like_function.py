import unittest
import sys
import os

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import app, db


class TestLikeFunction(unittest.TestCase):
    """좋아요 기능 통합 테스트"""

    def setUp(self):
        """각 테스트 전에 실행 - 테스트 클라이언트 및 테스트 데이터 준비"""
        self.app = app
        self.client = self.app.test_client()
        
        # 테스트용 영화 데이터 삽입
        self.test_movie_1 = {
            'title': '테스트영화1',
            'poster_url': 'http://test1.com',
            'info_url': 'http://info1.com',
            'open_year': 2020,
            'open_month': 1,
            'open_day': 1,
            'viewers': 1000000,
            'likes': 10,
            'trashed': False
        }
        self.test_movie_2 = {
            'title': '테스트영화2',
            'poster_url': 'http://test2.com',
            'info_url': 'http://info2.com',
            'open_year': 2021,
            'open_month': 5,
            'open_day': 15,
            'viewers': 2000000,
            'likes': 20,
            'trashed': False
        }
        
        db.movies.insert_one(self.test_movie_1)
        db.movies.insert_one(self.test_movie_2)

    def tearDown(self):
        """각 테스트 후에 실행 - 테스트 데이터 정리"""
        db.movies.delete_many({'title': {'$regex': '^테스트영화'}})

    def test_like_movie_success(self):
        """특정 영화의 좋아요를 1 증가시키는 테스트"""
        response = self.client.post('/api/like', data={'title_give': '테스트영화1'})
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['result'], 'success')
        self.assertEqual(data['msg'], '좋아요 완료!')
        
        # DB에서 해당 영화의 likes가 11로 증가했는지 확인
        movie = db.movies.find_one({'title': '테스트영화1'})
        self.assertEqual(movie['likes'], 11)

    def test_like_movie_multiple_times(self):
        """같은 영화에 여러 번 좋아요를 누르는 테스트"""
        # 첫 번째 좋아요
        self.client.post('/api/like', data={'title_give': '테스트영화1'})
        movie = db.movies.find_one({'title': '테스트영화1'})
        self.assertEqual(movie['likes'], 11)
        
        # 두 번째 좋아요
        self.client.post('/api/like', data={'title_give': '테스트영화1'})
        movie = db.movies.find_one({'title': '테스트영화1'})
        self.assertEqual(movie['likes'], 12)

    def test_like_different_movies(self):
        """서로 다른 영화에 좋아요를 누를 때 각각의 영화만 증가하는지 테스트"""
        # 영화1에 좋아요
        self.client.post('/api/like', data={'title_give': '테스트영화1'})
        movie1 = db.movies.find_one({'title': '테스트영화1'})
        movie2 = db.movies.find_one({'title': '테스트영화2'})
        self.assertEqual(movie1['likes'], 11)
        self.assertEqual(movie2['likes'], 20)  # 영화2는 변경 없음
        
        # 영화2에 좋아요
        self.client.post('/api/like', data={'title_give': '테스트영화2'})
        movie1 = db.movies.find_one({'title': '테스트영화1'})
        movie2 = db.movies.find_one({'title': '테스트영화2'})
        self.assertEqual(movie1['likes'], 11)  # 영화1은 변경 없음
        self.assertEqual(movie2['likes'], 21)

    def test_like_movie_not_found(self):
        """존재하지 않는 영화에 좋아요를 누르는 테스트"""
        response = self.client.post('/api/like', data={'title_give': '존재하지않는영화'})
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['result'], 'failure')
        self.assertEqual(data['msg'], '해당 영화를 찾을 수 없습니다.')

    def test_like_movie_no_title(self):
        """title_give를 전달하지 않는 테스트"""
        response = self.client.post('/api/like', data={})
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['result'], 'failure')
        self.assertEqual(data['msg'], '영화 제목이 전달되지 않았습니다.')

    def test_like_only_affects_one_movie(self):
        """좋아요가 다른 영화에 영향을 주지 않는지 확인하는 테스트"""
        # 초기 상태 저장
        all_movies_before = list(db.movies.find({'title': {'$regex': '^테스트영화'}}))
        total_likes_before = sum(m['likes'] for m in all_movies_before)
        
        # 영화1에 좋아요
        self.client.post('/api/like', data={'title_give': '테스트영화1'})
        
        # 전체 좋아요 합계가 정확히 1만 증가했는지 확인
        all_movies_after = list(db.movies.find({'title': {'$regex': '^테스트영화'}}))
        total_likes_after = sum(m['likes'] for m in all_movies_after)
        self.assertEqual(total_likes_after, total_likes_before + 1)


if __name__ == '__main__':
    unittest.main()
