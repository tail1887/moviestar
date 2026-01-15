FROM python:3.10-slim

WORKDIR /app

# 의존성 먼저 복사 (Docker 캐싱 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
