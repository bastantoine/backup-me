FROM python:3 AS builder

WORKDIR /app

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY pyproject.toml ./
COPY backup_me ./backup_me

RUN pip install --upgrade pip && \
    pip install .

FROM python:3-slim AS runtime

WORKDIR /app

COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

CMD ["backup-me"]
