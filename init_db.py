import re
import random
import requests
import os
import sys

from bs4 import BeautifulSoup
from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)

mongo_host = os.getenv('MONGO_HOST', 'localhost')
mongo_port = int(os.getenv('MONGO_PORT', 27017))
client = MongoClient(mongo_host, mongo_port)  # mongoDB 연결
db = client.dbjungle                      # 'dbjungle'라는 이름의 db를 만듭니다.


def insert_all():
    try:
        # URL을 읽어서 HTML를 받아오고,
        print("🌐 영화 데이터 스크래핑 시작...")
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        data = requests.get('https://search.daum.net/search?w=tot&q=역대관객순위&DA=MOR&rtmaxcoll=MOR', headers=headers, timeout=30)
        data.raise_for_status()  # HTTP 에러 체크
        
        # HTML을 BeautifulSoup이라는 라이브러리를 활용해 검색하기 용이한 상태로 만듦
        soup = BeautifulSoup(data.text, 'html.parser')

        # select를 이용해서, li들을 불러오기
        movies = soup.select('* c-list-doc > c-doc')
        print(f"📊 발견된 영화 요소: {len(movies)}개")
    except requests.RequestException as e:
        print(f"❌ 웹 스크래핑 실패: {e}")
        raise
    except Exception as e:
        print(f"❌ 초기화 중 오류 발생: {e}")
        raise
    # movies (li들) 의 반복문을 돌리기
    inserted_count = 0
    skipped_count = 0
    error_count = 0
    
    for movie in movies:
        try:
            # 영화 타이틀 정보를 추출한다.
            tag_element = movie.select_one('c-title')
            if not tag_element:
                skipped_count += 1
                continue
            title = tag_element.string.strip()

            # 영화 정보 URL 을 추출한다.
            info_url = f'https://search.daum.net/search{tag_element["data-href"]}'

            # 영화 포스터 이미지 URL 을 추출한다.
            tag_element = movie.select_one('c-thumb')
            if not tag_element:
                skipped_count += 1
                continue
            poster_url = tag_element['data-original-src']

            # 누적 관객수를 얻어낸다. "783,567명" 과 같은 형태가 된다.
            tag_element = movie.select_one('c-contents-desc')
            if not tag_element:
                skipped_count += 1
                continue
            viewers = tag_element.string
            viewers = viewers.replace('만', '0,000')
            viewers = re.findall(r'[0-9]+', viewers)
            viewers = ''.join(viewers)
            viewers = int(viewers)

            # 년도.월.일 형태에서 년도, 월, 일을 추출하기
            # (각각이 . 으로 구분되어있으므로 . 을 기준으로 split 한 뒤 각각을 문자형태에서 숫자형태로 변경해준다.)
            tag_element = movie.select_one('c-contents-desc-sub')
            if not tag_element:
                skipped_count += 1
                continue
            open_date = tag_element.string.replace('.', ' ').strip().replace(' ', '.')
            (open_year, open_month, open_day) = [int(element) for element in open_date.split('.')]


            # 평점을 이용하여, 좋아요수를 임의로 만든다
            likes = random.randrange(0, 100)

            # 존재하지 않는 영화인 경우만 추가한다.
            found = list(db.movies.find({'title': title}))
            if found:
                skipped_count += 1
                continue

            doc = {
                'title': title,
                'open_year': open_year,
                'open_month': open_month,
                'open_day': open_day,
                'viewers': viewers,
                'poster_url': poster_url,
                'info_url': info_url,
                'likes': likes,
                'trashed': False,
            }
            db.movies.insert_one(doc)
            inserted_count += 1
            print(f'✅ 완료 ({inserted_count}): {title} ({open_year}.{open_month}.{open_day}, 관객수: {viewers:,}명)')
        except Exception as e:
            error_count += 1
            print(f'⚠️ 영화 데이터 처리 중 오류: {e}')
            continue
    
    print(f"\n📊 스크래핑 결과:")
    print(f"  - 성공적으로 추가: {inserted_count}개")
    print(f"  - 건너뜀: {skipped_count}개")
    print(f"  - 오류: {error_count}개")


if __name__ == '__main__':
    try:
        print("🚀 DB 초기화 시작...")
        # 기존의 movies 콜렉션을 삭제하기
        db.movies.drop()
        print("🗑️ 기존 데이터 삭제 완료")

        # 영화 사이트를 scraping 해서 db 에 채우기
        insert_all()
        
        # 최종 확인
        final_count = db.movies.count_documents({})
        print(f"\n✅ DB 초기화 완료! 총 {final_count}개의 영화 데이터가 저장되었습니다.")
        
        if final_count == 0:
            print("⚠️ 경고: 저장된 영화 데이터가 없습니다!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ DB 초기화 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
