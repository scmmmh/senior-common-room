FROM nginx:latest

COPY docker/production/static/nginx.default.conf /etc/nginx/conf.d/default.conf

COPY src/frontend/public /usr/share/nginx/html/frontend
