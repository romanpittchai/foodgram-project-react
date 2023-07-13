if [ ! -f /app/.initialized ]; then
    apk add --upgrade --no-cache apk-tools
    apk update --no-cache
	apk add mc tree nano --no-cache

fi

exec "$@"