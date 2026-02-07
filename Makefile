.PHONY: dev-web dev-api export-data refresh-data deploy check-runtime-guardrails

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
