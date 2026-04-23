FROM python:latest
WORKDIR /app
CMD ["/bin/sh", "/app/start_server.sh"]
ENV DATABASE_PATH="/app/db/database.db"
RUN apt update && apt install -y nginx
COPY ./src/backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt --break-system-packages
COPY deploy/start_server.sh /app/start_server.sh
COPY deploy/nginx_config.conf /etc/nginx/nginx.conf
COPY ./src /app/src