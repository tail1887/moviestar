from bson import ObjectId # pymongo가 설치될 때 함께 설치됨. (install X)
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider

import json
import sys
import os


app = Flask(__name__)

# MongoDB 연결 시도 및 에러 처리
try:
    mongo_host = os.getenv('MONGO_HOST', 'localhost')
    mongo_port = int(os.getenv('MONGO_PORT', 27017))
    client = MongoClient(mongo_host, mongo_port, serverSelectionTimeoutMS=5000)
    # 연결 테스트
    client.admin.command('ping')
    db = client.dbjungle
    print("MongoDB 연결 성공")
except Exception as e:
    print(f"MongoDB 연결 실패: {e}")
    print("MongoDB 서비스가 실행 중인지 확인하세요.")
    sys.exit(1)


#####################################################################################
# 이 부분은 코드를 건드리지 말고 그냥 두세요. 코드를 이해하지 못해도 상관없는 부분입니다.
#
# ObjectId 타입으로 되어있는 _id 필드는 Flask 의 jsonify 호출시 문제가 된다.
# 이를 처리하기 위해서 기본 JsonEncoder 가 아닌 custom encoder 를 사용한다.
# Custom encoder 는 다른 부분은 모두 기본 encoder 에 동작을 위임하고 ObjectId 타입만 직접 처리한다.
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)


# 위에 정의되 custom encoder 를 사용하게끔 설정한다.
app.json = CustomJSONProvider(app)

# 여기까지 이해 못해도 그냥 넘어갈 코드입니다.
# #####################################################################################



#####
# 아래의 각각의 @app.route 은 RESTful API 하나에 대응됩니다.
# @app.route() 의 첫번째 인자는 API 경로,
# 생략 가능한 두번째 인자는 해당 경로에 적용 가능한 HTTP method 목록을 의미합니다.

# API #1: HTML 틀(template) 전달
#         틀 안에 데이터를 채워 넣어야 하는데 이는 아래 이어지는 /api/list 를 통해 이루어집니다.
@app.route('/')
def home():
    return render_template('index.html')


# API #2: 휴지통에 버려지지 않은 영화 목록을 반환합니다.
@app.route('/api/list', methods=['GET'])
def show_movies():
    try:
        # client 에서 요청한 정렬 방식이 있는지를 확인합니다. 없다면 기본으로 좋아요 순으로 정렬합니다.
        sortMode = request.args.get('sortMode', 'likes')

        # 1. db에서 trashed 가 False인 movies 목록을 검색합니다. 주어진 정렬 방식으로 정렬합니다.
        # 참고) find({},{}), sort()를 활용하면 됨.
        if sortMode == 'likes':
            movies = list(db.movies.find({'trashed': False}, {}).sort('likes', -1))  # 좋아요 많은 순
        elif sortMode == 'viewers':
            movies = list(db.movies.find({'trashed': False}, {}).sort('viewers', -1))  # 관객수 많은 순
        elif sortMode == 'date':
            # 개봉일 순서: 연도 → 월 → 일 순으로 내림차순 정렬 (최신순)
            movies = list(db.movies.find({'trashed': False}, {}).sort([('open_year', -1), ('open_month', -1), ('open_day', -1)]))
        else:
            return jsonify({'result': 'failure', 'msg': '지원하지 않는 정렬 방식입니다.'})

        # 2. 성공하면 success 메시지와 함께 movies_list 목록을 클라이언트에 전달합니다.
        return jsonify({'result': 'success', 'movies_list': movies})
    except Exception as e:
        print(f"영화 목록 조회 중 에러 발생: {e}")
        return jsonify({'result': 'failure', 'msg': '영화 목록을 불러오는 중 오류가 발생했습니다.'})


# API #2-1: 휴지통에 있는 영화 목록을 반환합니다.
@app.route('/api/list/trash', methods=['GET'])
def show_trashed_movies():
    try:
        # client 에서 요청한 정렬 방식이 있는지를 확인합니다. 없다면 기본으로 좋아요 순으로 정렬합니다.
        sortMode = request.args.get('sortMode', 'likes')

        # 1. db에서 trashed 가 True인 movies 목록을 검색합니다.
        if sortMode == 'likes':
            movies = list(db.movies.find({'trashed': True}, {}).sort('likes', -1))  # 좋아요 많은 순
        elif sortMode == 'viewers':
            movies = list(db.movies.find({'trashed': True}, {}).sort('viewers', -1))  # 관객수 많은 순
        elif sortMode == 'date':
            # 개봉일 순서: 연도 → 월 → 일 순으로 내림차순 정렬 (최신순)
            movies = list(db.movies.find({'trashed': True}, {}).sort([('open_year', -1), ('open_month', -1), ('open_day', -1)]))
        else:
            return jsonify({'result': 'failure', 'msg': '지원하지 않는 정렬 방식입니다.'})

        # 2. 성공하면 success 메시지와 함께 movies_list 목록을 클라이언트에 전달합니다.
        return jsonify({'result': 'success', 'movies_list': movies})
    except Exception as e:
        print(f"휴지통 목록 조회 중 에러 발생: {e}")
        return jsonify({'result': 'failure', 'msg': '휴지통 목록을 불러오는 중 오류가 발생했습니다.'})

# API #3: 영화에 좋아요 숫자를 하나 올립니다.
@app.route('/api/like', methods=['POST'])
def like_movie():
    try:
        # 1. 클라이언트로부터 title_give를 받습니다.
        title_receive = request.form.get('title_give')
        
        # 2. 입력값 검증
        if not title_receive:
            return jsonify({'result': 'failure', 'msg': '영화 제목이 전달되지 않았습니다.'})
        
        # 3. movies 목록에서 해당 제목의 영화를 찾습니다.
        movie = db.movies.find_one({'title': title_receive})
        
        if not movie:
            return jsonify({'result': 'failure', 'msg': '해당 영화를 찾을 수 없습니다.'})
        
        # 4. movie의 likes에 1을 더해준 new_likes 변수를 만듭니다.
        new_likes = movie['likes'] + 1

        # 5. movies 목록에서 해당 영화의 likes를 new_likes로 변경합니다.
        result = db.movies.update_one(
            {'title': title_receive},
            {'$set': {'likes': new_likes}}
        )

        # 6. 하나의 영화만 영향을 받아야 하므로 result.modified_count가 1이면 success를 보냅니다.
        if result.modified_count == 1:
            return jsonify({'result': 'success', 'msg': '좋아요 완료!'})
        else:
            return jsonify({'result': 'failure', 'msg': '좋아요 처리에 실패했습니다.'})
    except Exception as e:
        print(f"좋아요 처리 중 에러 발생: {e}")
        return jsonify({'result': 'failure', 'msg': '좋아요 처리 중 오류가 발생했습니다.'})


# API #4: 영화를 휴지통으로 보냅니다 (Soft Delete).
@app.route('/api/delete', methods=['POST'])
def delete_movie():
    try:
        # 1. 클라이언트로부터 title_give를 받습니다.
        title_receive = request.form.get('title_give')
        
        # 2. 입력값 검증
        if not title_receive:
            return jsonify({'result': 'failure', 'msg': '영화 제목이 전달되지 않았습니다.'})
        
        # 3. movies 목록에서 해당 제목의 영화를 찾아 trashed를 True로 변경합니다.
        result = db.movies.update_one(
            {'title': title_receive},
            {'$set': {'trashed': True}}
        )
        
        # 4. 하나의 영화만 영향을 받아야 하므로 result.modified_count가 1이면 success를 보냅니다.
        if result.modified_count == 1:
            return jsonify({'result': 'success', 'msg': '삭제 완료!'})
        else:
            return jsonify({'result': 'failure', 'msg': '해당 영화를 찾을 수 없거나 이미 삭제되었습니다.'})
    except Exception as e:
        print(f"삭제 처리 중 에러 발생: {e}")
        return jsonify({'result': 'failure', 'msg': '삭제 처리 중 오류가 발생했습니다.'})


if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5000, debug=True)