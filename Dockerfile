FROM python:3.11-slim

RUN mkdir /app
WORKDIR /app

ENV PYTHONPATH=/app:${PYTHONPATH}

COPY poetry.lock pyproject.toml /app

RUN pip install poetry
RUN poetry install

COPY . /app

CMD ["poetry", "run", "python", "bot"]
