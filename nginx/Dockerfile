FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf

# for prod:
COPY prod.conf /etc/nginx/conf.d/default.conf
