FROM python:3.12-slim-bookworm

# Prepare Poetry env
RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Prepare external dependencies
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt install -y --no-install-recommends lsb-release gnupg wget && \
    wget --no-check-certificate -c https://repo.mysql.com/mysql-apt-config_0.8.32-1_all.deb && \
    dpkg -i mysql-apt-config_0.8.32-1_all.deb && \
    apt update && \
    apt install -y --no-install-recommends mysql-client postgresql-client && \
    apt autoremove

WORKDIR /app
ADD pyproject.toml poetry.lock ./

RUN poetry install --without tests --no-root && rm -rf $POETRY_CACHE_DIR

ENV PATH="/app/.venv/bin:$PATH"

ADD backup_me/ backup_me/

WORKDIR /

ENTRYPOINT ["python", "-m", "backup_me.main"]
