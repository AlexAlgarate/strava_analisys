FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

ADD https://astral.sh/uv/0.6.6/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"
ADD . /app
WORKDIR /app

COPY . .

# RUN python -m venv /app/venv && \
#     /app/venv/bin/pip install --no-cache-dir --upgrade pip && \
#     /app/venv/bin/pip install -r requirements.txt

# CMD ["/app/venv/bin/python", "main.py"]
CMD ["uv", "run", "main.py"]
