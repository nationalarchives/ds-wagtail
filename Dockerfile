FROM python:3.9
LABEL maintainer="dan@numiko.com"

ENV PYTHONUNBUFFERED 1

# Using /app ensures the paths are identical to platform.sh
WORKDIR /app/

COPY poetry.lock /app/
COPY pyproject.toml /app/
RUN python -m pip install pip==21.3.1
RUN pip install poetry==1.1.12
RUN poetry install

EXPOSE 8000
