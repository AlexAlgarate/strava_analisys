FROM python:3.13-slim-trixie AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12.11 /uv /bin/uv

ENV UV_PYTHON_DOWNLOADS=never
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project


FROM python:3.13-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY main.py ./
COPY src ./src

CMD ["/app/.venv/bin/python", "main.py"]
