FROM python:3.13-slim-trixie AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12.11 /uv /bin/uv

ENV UV_PYTHON_DOWNLOADS=never
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project


FROM python:3.13-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd --gid 10001 strava \
    && useradd --uid 10001 --gid strava --create-home \
        --home-dir /home/strava --shell /usr/sbin/nologin strava \
    && install -d --owner=strava --group=strava --mode=0750 /app

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY main.py ./
COPY src ./src

USER 10001:10001

CMD ["/app/.venv/bin/python", "main.py"]
