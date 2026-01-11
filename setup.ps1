# 1. 인코딩 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "🚀 requirements.txt를 참조하여 프로젝트 세팅을 시작합니다..." -ForegroundColor Cyan

# 2. 필수 폴더 생성
New-Item -ItemType Directory -Force -Path "static", "templates", "tests"

# 3. 가상환경 생성 (없을 경우에만)
if (!(Test-Path "venv")) {
    Write-Host "📦 가상환경 생성 중..." -ForegroundColor Yellow
    python -m venv venv
}

# 4. 라이브러리 설치 (requirements.txt 참조)
if (Test-Path "requirements.txt") {
    Write-Host "📥 requirements.txt에 명시된 패키지를 설치합니다..." -ForegroundColor Cyan
    .\venv\Scripts\python.exe -m pip install --upgrade pip
    .\venv\Scripts\python.exe -m pip install -r requirements.txt
} else {
    Write-Host "❌ 에러: requirements.txt 파일이 폴더에 없습니다!" -ForegroundColor Red
    exit
}

# 5. 기본 파일들 생성 (이미 있으면 덮어쓰지 않음)
if (!(Test-Path "app.py")) {
    $appContent = "from flask import Flask`napp = Flask(__name__)`n@app.route('/')`ndef home(): return 'Hello'`nif __name__ == '__main__': app.run(debug=True)"
    $appContent | Out-File -FilePath "app.py" -Encoding utf8
}

Write-Host "`n✨ 세팅 완료! '.\venv\Scripts\activate' 후 시작하세요." -ForegroundColor Green