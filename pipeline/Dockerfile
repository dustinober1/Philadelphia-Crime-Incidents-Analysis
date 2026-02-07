FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
# Install dependencies before source copy so warm builds can reuse this layer.
RUN pip install --no-cache-dir . typer pydantic pydantic-settings pyyaml

COPY analysis /app/analysis
COPY config /app/config
COPY pipeline /app/pipeline
COPY api /app/api
COPY data/boundaries /app/data/boundaries
COPY data/external /app/data/external

RUN chmod +x /app/pipeline/compose_entrypoint.sh

CMD ["/app/pipeline/compose_entrypoint.sh"]
