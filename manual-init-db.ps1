# EC2 수동 DB 초기화 스크립트
Write-Host "🔑 EC2 SSH 접속 및 DB 초기화 중..." -ForegroundColor Cyan

ssh -i "C:\Users\tail1\Desktop\tail1887.pem" ubuntu@ec2-52-78-228-235.ap-northeast-2.compute.amazonaws.com @"
cd moviestar
echo '📊 데이터베이스 초기화 시작...'
sudo docker-compose exec -T app python init_db.py
echo '✅ 초기화 완료! 컨테이너 상태 확인:'
sudo docker-compose ps
echo '🌐 애플리케이션 로그 확인:'
sudo docker-compose logs --tail=20 app
"@
