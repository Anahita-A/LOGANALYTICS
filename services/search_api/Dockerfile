# services/search_api/Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY app.py .

RUN pip install flask flask-cors minio

CMD ["python", "app.py"]