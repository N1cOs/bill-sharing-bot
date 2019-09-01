FROM python:3.7-alpine

COPY . /app
WORKDIR /app

RUN apk add --no-cache \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    && pip install --no-cache-dir -r requirements.txt  \
    && apk del --no-cache gcc python3-dev musl-dev

CMD ["gunicorn", "-b", "0.0.0.0:8000", "main:app"]
