FROM nginx:1.23.1-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d
COPY certs/server.crt /etc/nginx/certs/server.crt
COPY certs/server.key /etc/nginx/certs/server.key

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]

ENV SHELL /bin/sh