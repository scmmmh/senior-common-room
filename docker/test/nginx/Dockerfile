FROM nginx:latest

RUN apt-get update && apt-get install ssl-cert

COPY nginx.default.conf /etc/nginx/conf.d/default.conf
