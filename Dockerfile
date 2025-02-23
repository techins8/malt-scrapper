FROM python:3.12-slim AS builder

WORKDIR /code

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade pip; \
    pip install --no-cache-dir --upgrade -r /code/requirements.txt

FROM builder AS app

WORKDIR /code

COPY . /code

RUN pip install --no-cache-dir -r requirements.txt && \
    mkdir -p migrations/versions

EXPOSE 80

CMD ["uvicorn", "api:app", "--reload", "--app-dir", "app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80", "--log-level", "debug"]