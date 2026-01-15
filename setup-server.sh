#!/bin/bash

# EC2 서버 초기 설정 스크립트
# Docker 및 Docker Compose 설치, 권한 설정

set -e  # 에러 발생 시 즉시 중단

echo "🚀 서버 초기 설정 시작..."

# Docker 설치 여부 확인
if ! command -v docker &> /dev/null; then
    echo "📦 Docker 설치 중..."
    sudo apt update
    sudo apt install -y docker.io
    
    # Docker 서비스 시작 및 부팅 시 자동 시작 설정
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # 현재 사용자를 docker 그룹에 추가
    sudo usermod -aG docker $USER
    
    echo "✅ Docker 설치 완료"
else
    echo "✅ Docker 이미 설치되어 있음"
fi

# Docker Compose 설치 여부 확인
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Docker Compose 설치 중..."
    sudo apt install -y docker-compose
    echo "✅ Docker Compose 설치 완료"
else
    echo "✅ Docker Compose 이미 설치되어 있음"
fi

# Git 설치 여부 확인
if ! command -v git &> /dev/null; then
    echo "📦 Git 설치 중..."
    sudo apt install -y git
    echo "✅ Git 설치 완료"
else
    echo "✅ Git 이미 설치되어 있음"
fi

echo "🎉 서버 초기 설정 완료!"
echo "⚠️  주의: Docker 그룹 권한 적용을 위해 재로그인이 필요할 수 있습니다."
