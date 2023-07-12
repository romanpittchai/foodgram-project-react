FROM python:3.9-slim-bullseye

ARG some_variable_name

WORKDIR /app

RUN python3 -m pip install --upgrade pip --no-cache-dir

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind","0.0.0.0:8000", "foodgram_backend.wsgi:application"]

RUN apt-get update && apt-get install -y make mc tree nano

RUN python3 manage.py makemigrations

RUN python3 manage.py migrate

RUN python3 manage.py loadcsv

RUN make create_superuser \
    && make create_user