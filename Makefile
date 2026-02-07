.PHONY: dev-web dev-api export-data refresh-data deploy check-runtime-guardrails clean-pyc clean-imports clean-reports clean-build clean-all check-clean scan-dead-code

dev-web:
	cd web && npm run dev

dev-api:
	uvicorn api.main:app --reload

export-data:
	python -m pipeline.export_data --output-dir api/data

refresh-data:
	python -m pipeline.refresh_data --output-dir api/data

deploy:
	firebase deploy && gcloud run deploy philly-crime-api --source api/ --region us-east1 --allow-unauthenticated

check-runtime-guardrails:
	./scripts/validate_runtime_guardrails.sh

# Cleanup targets
clean-pyc:
	@echo "Removing Python artifacts..."
	pyclean .
	@echo "Python artifacts removed"

clean-imports:
	@echo "Removing unused imports..."
	autoflake --remove-all-unused-imports --recursive --in-place analysis/ api/ pipeline/
	@echo "Unused imports removed"

clean-reports:
	@echo "Removing coverage reports and cache..."
	rm -rf htmlcov/
	rm -f .coverage .coverage.*
	rm -rf .pytest_cache/
	@echo "Reports cleaned"

clean-build:
	@echo "Removing build artifacts..."
	rm -rf *.egg-info/ dist/ build/
	@echo "Build artifacts removed"

clean-all: clean-pyc clean-imports clean-reports clean-build
	@echo "All cleanup operations complete"

# Safety gate check
check-clean:
	@echo "=== Safety Gate: Git Status ==="
	@git status --short
	@echo ""
	@echo "=== Safety Gate: Imports ==="
	@python -c "import analysis, api, pipeline; print('All packages import OK')"
	@echo ""
	@echo "=== Safety Gate: Quick Tests ==="
	@pytest tests/ --fast --maxfail=1 -q

# Dead code scan (read-only, no deletions)
scan-dead-code:
	@echo "Scanning for dead code (read-only)..."
	@vulture analysis/ api/ pipeline/ --min-confidence 90 --sort-by-size
	@echo ""
	@echo "To generate full report: vulture analysis/ api/ pipeline/ > vulture-report.txt"
