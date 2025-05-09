FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY consumer.py .

CMD ["sh", "-c", "echo 'Waiting for Kafka...'; \
  while ! nc -z kafka 9092; do sleep 1; done; \
  echo 'Kafka is up! Starting consumer...'; \
  python consumer.py"]

