include .env

export

static:
	python3 manage.py collectstatic

create_superuser:
	python3 manage.py createsuperuser --noinput

create_user:
	python3 manage.py shell -c "from users.models import User; \
		User.objects.create_user(username='$(DJANGO_USERNAME)', \
		email='$(DJANGO_EMAIL)', \
		first_name='$(DJANGO_FIRST_NAME)', \
		last_name='$(DJANGO_LAST_NAME)', \
		password='$(DJANGO_PASSWORD)')"

del_env:
	rm .env

migrate_load:
	python3 manage.py makemigrations \
    	&& python3 manage.py migrate \
    	&& python3 manage.py loadcsv

copy_static:
	cp -r /app/collected_static/. /backend_static/static/


