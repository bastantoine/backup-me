FROM python:3.12 as builder

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app
ADD pyproject.toml poetry.lock ./

RUN poetry install --without tests --no-root && rm -rf $POETRY_CACHE_DIR

FROM python:3.12-slim as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

ADD backup_me/ backup_me/

WORKDIR /

ENTRYPOINT ["python", "-m", "backup_me.main"]
