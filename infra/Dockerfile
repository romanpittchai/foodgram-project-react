FROM nginx:1.22.1-alpine-slim

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

RUN "./entrypoint.sh"
 