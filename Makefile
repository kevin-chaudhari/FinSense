# FinSense AI — Makefile
# Convenience commands for development

.PHONY: dev dev-backend dev-frontend install install-gpu test lint gpu-check clean docker docker-gpu help

help:
	@echo ""
	@echo "  FinSense AI — Available Commands"
	@echo "  ─────────────────────────────────"
	@echo "  make dev           Start both backend + frontend (requires 2 terminals)"
	@echo "  make dev-backend   Start FastAPI backend (port 8000)"
	@echo "  make dev-frontend  Start Next.js frontend (port 3000)"
	@echo "  make install       Install CPU dependencies"
	@echo "  make install-gpu   Install GPU/CUDA dependencies"
	@echo "  make gpu-check     Run GPU environment verification"
	@echo "  make test          Run backend tests"
	@echo "  make lint          Run code linting (backend + frontend)"
	@echo "  make docker        Build and run with Docker (CPU)"
	@echo "  make docker-gpu    Build and run with Docker (GPU)"
	@echo "  make clean         Clean build artifacts and caches"
	@echo ""

dev-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

install-gpu:
	pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
	cd backend && pip install -r requirements-gpu.txt
	pip uninstall faiss-cpu -y; pip install faiss-gpu

gpu-check:
	cd backend && python scripts/setup_gpu.py

test:
	cd backend && pytest tests/ -v --tb=short

test-cov:
	cd backend && pytest tests/ -v --cov=app --cov-report=html --cov-report=term

lint:
	cd backend && python -m ruff check app/ --fix
	cd frontend && npm run lint

type-check:
	cd frontend && npm run type-check

docker:
	docker compose up --build

docker-gpu:
	docker compose -f docker-compose.gpu.yml up --build

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf frontend/.next frontend/node_modules/.cache
	@echo "Clean complete"
