FROM python:3.9-slim-bullseye

WORKDIR /app

RUN python3 -m pip install --upgrade pip --no-cache-dir

COPY requirements.txt .

COPY . .

CMD ["gunicorn", "--bind","0.0.0.0:8000", "foodgram_backend.wsgi:application"]