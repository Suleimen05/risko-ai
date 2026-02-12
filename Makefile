.PHONY: help install dev build docker-up docker-down clean

help:
	@echo "TrendScout Clone - Available commands:"
	@echo "  make install     - Install all dependencies"
	@echo "  make dev         - Start development servers"
	@echo "  make docker-up   - Start all services with Docker"
	@echo "  make docker-down - Stop all Docker services"
	@echo "  make clean       - Clean build artifacts"

install:
	@echo "Installing client dependencies..."
	cd client && npm install
	@echo "Installing server dependencies..."
	cd server && pip install -r requirements.txt
	@echo "Installing ML service dependencies..."
	cd ml-service && pip install -r requirements.txt

dev:
	@echo "Starting all services in development mode..."
	@echo "Note: Run each in a separate terminal or use Docker Compose"
	@echo "Terminal 1: cd client && npm run dev"
	@echo "Terminal 2: cd server && uvicorn app.main:app --reload"
	@echo "Terminal 3: cd ml-service && uvicorn app.main:app --reload --port 8001"

docker-up:
	docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:5173"
	@echo "Backend API: http://localhost:8000"
	@echo "ML Service: http://localhost:8001"

docker-down:
	docker-compose down

clean:
	rm -rf client/node_modules client/dist
	rm -rf server/__pycache__ server/**/__pycache__
	rm -rf ml-service/__pycache__ ml-service/**/__pycache__
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
