FROM nginx:1.22.1-alpine-slim

RUN apk add --upgrade --no-cache apk-tools \
		&& apk update --no-cache \
		&& apk add mc tree nano

COPY nginx.conf /etc/nginx/conf.d/default.conf
