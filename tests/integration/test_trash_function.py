"""
통합 테스트: 휴지통 기능
- POST /api/delete 엔드포인트 테스트
- GET /api/list/trash 엔드포인트 테스트
"""
import unittest
import sys
import os

# 프로젝트 루트 디렉토리를 Python path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import app, db


class TestTrashFunction(unittest.TestCase):
    """휴지통 기능 통합 테스트"""

    @classmethod
    def setUpClass(cls):
        """테스트 클래스 시작 전 한 번 실행"""
        app.config['TESTING'] = True
        cls.client = app.test_client()

    def setUp(self):
        """각 테스트 전 실행 - 테스트용 영화 데이터 추가"""
        # 테스트용 영화 데이터 삽입
        self.test_movie = {
            'title': '테스트영화_휴지통용',
            'poster_url': 'https://test.com/poster.jpg',
            'info_url': 'https://test.com/info',
            'open_year': 2024,
            'open_month': 1,
            'open_day': 1,
            'viewers': 1000000,
            'likes': 10,
            'trashed': False
        }
        db.movies.insert_one(self.test_movie.copy())

    def tearDown(self):
        """각 테스트 후 실행 - 테스트 데이터 삭제"""
        db.movies.delete_many({'title': '테스트영화_휴지통용'})

    def test_delete_movie_success(self):
        """영화 삭제(휴지통 이동) 성공 테스트"""
        response = self.client.post('/api/delete', data={
            'title_give': '테스트영화_휴지통용'
        })
        
        data = response.get_json()
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['result'], 'success')
        self.assertEqual(data['msg'], '삭제 완료!')
        
        # DB에서 trashed 상태 확인
        movie = db.movies.find_one({'title': '테스트영화_휴지통용'})
        self.assertTrue(movie['trashed'])

    def test_delete_movie_not_found(self):
        """존재하지 않는 영화 삭제 시도 테스트"""
        response = self.client.post('/api/delete', data={
            'title_give': '존재하지않는영화'
        })
        
        data = response.get_json()
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['result'], 'failure')
        self.assertIn('찾을 수 없거나', data['msg'])

    def test_delete_movie_no_title(self):
        """영화 제목 없이 삭제 시도 테스트"""
        response = self.client.post('/api/delete', data={})
        
        data = response.get_json()
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['result'], 'failure')
        self.assertIn('전달되지 않았습니다', data['msg'])

    def test_list_trash_empty(self):
        """휴지통이 비어있을 때 목록 조회 테스트"""
        response = self.client.get('/api/list/trash')
        
        data = response.get_json()
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['result'], 'success')
        self.assertIsInstance(data['movies_list'], list)

    def test_list_trash_with_movies(self):
        """휴지통에 영화가 있을 때 목록 조회 테스트"""
        # 먼저 영화를 휴지통으로 보냄
        self.client.post('/api/delete', data={
            'title_give': '테스트영화_휴지통용'
        })
        
        # 휴지통 목록 조회
        response = self.client.get('/api/list/trash')
        data = response.get_json()
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['result'], 'success')
        self.assertIsInstance(data['movies_list'], list)
        
        # 휴지통에 테스트 영화가 있는지 확인
        trash_titles = [movie['title'] for movie in data['movies_list']]
        self.assertIn('테스트영화_휴지통용', trash_titles)

    def test_list_does_not_show_trashed_movies(self):
        """일반 목록에서 삭제된 영화가 보이지 않는지 테스트"""
        # 영화를 휴지통으로 보냄
        self.client.post('/api/delete', data={
            'title_give': '테스트영화_휴지통용'
        })
        
        # 일반 목록 조회
        response = self.client.get('/api/list')
        data = response.get_json()
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['result'], 'success')
        
        # 일반 목록에 삭제된 영화가 없는지 확인
        normal_titles = [movie['title'] for movie in data['movies_list']]
        self.assertNotIn('테스트영화_휴지통용', normal_titles)


if __name__ == '__main__':
    unittest.main()
