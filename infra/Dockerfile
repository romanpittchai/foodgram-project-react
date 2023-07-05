FROM nginx:1.22.1-alpine-slim

RUN apk add --upgrade apk-tools

RUN apk update

RUN apk add mc tree nano

COPY nginx.conf /etc/nginx/conf.d/default.conf
