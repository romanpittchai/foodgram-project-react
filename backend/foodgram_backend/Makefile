backjob:
	./backendjob.sh

migrate:
	python3 manage.py makemigrations

migrate-db:
	python3 manage.py migrate

create-su:
	python3 manage.py createsuperuser --noinput

load-db:
	python3 manage.py loadcsv

collect-static:
	python3 manage.py collectstatic

start-local:
	migrate migrate-db create-su create-us load-db collect-static

clear-bd:
	python3 manage.py clearbd

flake:
	flake8 --exclude venv,migrations,settings.py, manage.py

up-compose:
	docker-compose up -d

build-compose:
	docker-compose up -d --build

stop-compose:
	docker-compose stop

start-compose:
	docker-compose start

migrate-compose:
	docker-compose exec -it web python3 manage.py makemigrations

migrate-db-compose:
	docker-compose exec -it web python3 manage.py migrate

create-su-compose:
	docker-compose exec -it web python3 manage.py createsuperuser --noinput

load-db-compose:
	docker-compose exec -it web python3 manage.py loadcsv

clear-bd-compose:
	docker-compose exec -it web python3 manage.py clearbd
