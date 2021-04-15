FROM python:3.9
LABEL maintainer="dan@numiko.com"

ENV PYTHONUNBUFFERED 1

# Using /app ensures the paths are identical to platform.sh
WORKDIR /app/

COPY poetry.lock /app/
COPY pyproject.toml /app/
RUN pip install poetry
RUN poetry install

EXPOSE 8000
