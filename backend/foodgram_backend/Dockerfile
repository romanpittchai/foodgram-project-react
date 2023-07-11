FROM python:3.9-slim-bullseye

WORKDIR /app

RUN python3 -m pip install --upgrade pip --no-cache-dir

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN python3 manage.py makemigrations

RUN python3 manage.py migrate

RUN python3 manage.py loadcsv

CMD ["gunicorn", "--bind","0.0.0.0:8000", "foodgram_backend.wsgi:application"]