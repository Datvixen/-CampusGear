FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=10000

EXPOSE 10000


CMD ["sh", "-c", "python -c 'from app import init_db; init_db()' && exec gunicorn --bind 0.0.0.0:${PORT:-10000} app:app"]

