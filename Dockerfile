FROM python:3.12

WORKDIR /app

COPY . .

RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /app/venv/bin/pip install -r requirements.txt

CMD ["/app/venv/bin/python", "main.py"]