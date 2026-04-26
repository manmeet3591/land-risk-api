.PHONY: start-backend start-frontend dev

start-backend:
	cd backend && source venv/bin/activate && python3 main.py

start-frontend:
	cd frontend && npm run dev

dev:
	@echo "Starting backend and frontend..."
	@make -j 2 start-backend start-frontend
