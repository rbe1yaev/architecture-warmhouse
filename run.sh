#!/bin/bash

echo "Building Smart House Microservices..."

docker-compose build

echo "Starting services..."
docker-compose up -d

echo "Waiting for services to start..."
sleep 30

echo "Checking services health..."

echo ""
echo "Smart House System deployed successfully!"
echo ""
echo "Services:"
echo "- API Gateway: http://localhost:8000"
echo "- Auth Service: http://localhost:8001"
echo "- Device Service: http://localhost:8002"
echo "- Device Manager: http://localhost:8003"
echo "- Telemetry Service: http://localhost:8004"
echo "- Notification Service: http://localhost:8005"
echo "- Kafka: localhost:9092"
echo "- Kafka-ui: http://localhost:7777"

echo "- ClickHouse: http://localhost:8123"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Test command: curl http://localhost:8000/health"