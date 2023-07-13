FROM nginx:1.22.1-alpine-slim

RUN chmod +x entrypoint.sh

RUN "./entrypoint.sh"

COPY nginx.conf /etc/nginx/conf.d/default.conf
