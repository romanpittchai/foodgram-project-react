FROM nginx:1.22.1-alpine-slim

COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY gatewayjob.sh .

RUN chmod +x gatewayjob.sh

RUN "./gatewayjob.sh"
 