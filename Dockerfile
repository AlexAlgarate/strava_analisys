FROM python:3.13-slim-trixie@sha256:9d2e5553305c7c7b0097999bb17187c69b921ccd6bc9d40e4bb5ebe652c00285 AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12.11@sha256:79c6f4776b851471cc73b7d21d0cc834bb94383c292e83640d27eff512864df7 /uv /bin/uv

ENV UV_PYTHON_DOWNLOADS=never
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project


FROM python:3.13-slim-trixie@sha256:9d2e5553305c7c7b0097999bb17187c69b921ccd6bc9d40e4bb5ebe652c00285

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    XDG_STATE_HOME=/data/state

RUN groupadd --gid 10001 strava \
    && useradd --uid 10001 --gid strava --create-home \
        --home-dir /home/strava --shell /usr/sbin/nologin strava \
    && install -d --owner=root --group=strava --mode=0550 /app \
    && install -d --owner=strava --group=strava --mode=0700 /data

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY main.py ./
COPY src ./src

USER 10001:10001
WORKDIR /data

CMD ["/app/.venv/bin/python", "/app/main.py"]
