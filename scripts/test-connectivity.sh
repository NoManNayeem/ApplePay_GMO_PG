#!/bin/sh
# Test connectivity between frontend and backend

echo "Testing Backend Connectivity..."
echo "================================"
echo "Testing HTTPS backend..."
curl -k https://localhost:8443/admin/ -I || echo "Backend HTTPS not accessible"

echo ""
echo "Testing HTTP backend..."
curl http://localhost:8000/admin/ -I || echo "Backend HTTP not accessible"

echo ""
echo "Testing Frontend Connectivity..."
echo "=================================="
echo "Testing HTTPS frontend..."
curl -k https://localhost:3443/ -I || echo "Frontend HTTPS not accessible"

echo ""
echo "Testing HTTP frontend..."
curl http://localhost:3000/ -I || echo "Frontend HTTP not accessible"

echo ""
echo "Testing Backend API Endpoint..."
echo "================================="
curl -k https://localhost:8443/api/payments/merchant-session/ -I || echo "API endpoint not accessible"

echo ""
echo "Connectivity test complete!"

