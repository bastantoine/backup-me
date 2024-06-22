FROM python:3.12

RUN pip install poetry

WORKDIR /app
ADD pyproject.toml poetry.lock ./
# ADD poetry.lock .
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

ADD backup_me/ backup_me/
RUN poetry install

WORKDIR /
COPY docker-entrypoint.sh .

ENTRYPOINT ["backup-me"]
