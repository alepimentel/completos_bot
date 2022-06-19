FROM python:3.10-slim

RUN mkdir /app
WORKDIR /app

COPY poetry.lock pyproject.toml /app

RUN pip install poetry
RUN poetry install

COPY . /app

ENTRYPOINT ["./bin/entrypoint.sh"]
