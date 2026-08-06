FROM python:3 AS builder

WORKDIR /app

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY pyproject.toml ./
COPY backup_me ./backup_me

RUN pip install --upgrade pip && \
    pip install .

FROM python:3-slim AS mysql-runtime

RUN apt-get update && \
    apt-get install -y default-mysql-client && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

CMD ["backup-me"]
