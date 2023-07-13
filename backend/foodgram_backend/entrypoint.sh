
if [ ! -f /app/.initialized ]; then
	python3 manage.py makemigrations
	python3 manage.py migrate
	python3 manage.py loadcsv

	export $(grep -v '^#' .env | xargs)

	python3 manage.py createsuperuser --noinput

	python3 manage.py shell <<EOF
from users.models import User;
User.objects.create_user(username='$DJANGO_USERNAME', email='$DJANGO_EMAIL', first_name='$DJANGO_FIRST_NAME', last_name='$DJANGO_LAST_NAME', password='$DJANGO_PASSWORD')
EOF
	python3 manage.py collectstatic
	cp -r /app/collected_static/. /backend_static/

	touch /app/.initialized
	rm .env
fi

exec "$@"