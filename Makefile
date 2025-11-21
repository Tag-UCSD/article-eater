.PHONY: dev test manifest
dev:
	@echo "No app/ detected. If you add FastAPI at app/main.py, run: uvicorn app.main:app --reload"
test:
	pytest -q
manifest:
	python scripts/manifest_sha256.py