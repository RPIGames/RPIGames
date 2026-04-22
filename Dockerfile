FROM python:3.14
WORKDIR /app
COPY ./src/backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY ./src /app/src
CMD ["fastapi", "run", "src/backend/main.py", "--port", "80"]
