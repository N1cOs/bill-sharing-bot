FROM python:3.7-alpine

COPY . /app
WORKDIR /app

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    && pip install --no-cache-dir -r requirements.txt  \
    && apk del --no-cache .build-deps

CMD ["gunicorn", "-b", "0.0.0.0:8000", "main:app"]
