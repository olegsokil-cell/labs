#!/bin/bash

echo "=========================================="
echo "DNS Attack Lab - Setup Script"
echo "=========================================="
echo

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

echo "[1/4] Building Docker containers..."
docker-compose build

echo
echo "[2/4] Starting containers..."
docker-compose up -d

echo
echo "[3/4] Waiting for DNS server to start..."
sleep 5

echo
echo "[4/4] Verifying setup..."
echo

# Test DNS resolution
echo "Testing DNS resolution for www.example.com..."
docker exec user-machine dig www.example.com @10.9.0.16 +short

echo
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo
echo "Containers running:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo
echo "Quick Start Commands:"
echo "  - Access attacker: docker exec -it attacker bash"
echo "  - Access DNS server: docker exec -it dns-server bash"
echo "  - Access user: docker exec -it user-machine bash"
echo
echo "  - Flush DNS cache: docker exec dns-server rndc flush"
echo "  - View DNS cache: docker exec dns-server rndc dumpdb -cache"
echo
echo "Ready to start attacks! See README.md for task instructions."
echo
