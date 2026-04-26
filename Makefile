.PHONY: start-backend start-frontend dev

start-backend:
	cd backend && source venv/bin/activate && export DYLD_LIBRARY_PATH=/opt/homebrew/opt/gdal/lib:$$DYLD_LIBRARY_PATH && python main.py

start-frontend:
	cd frontend && npm run dev

dev:
	@echo "Starting backend and frontend..."
	@make -j 2 start-backend start-frontend
