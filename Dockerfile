FROM python:3.13-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY . .

RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    mkdir -p /app/src/app/uploads/photos && \
    chown -R appuser:appuser /app

USER appuser

ENV PYTHONPATH=/app/src \
    PATH="/app/.venv/bin:$PATH"

CMD ["sh", "-c", "alembic upgrade head && python src/app/main.py"]
