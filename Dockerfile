FROM python:3.11
LABEL maintainer="dan@numiko.com"

ARG POETRY_HOME=/opt/poetry

EXPOSE 8000

ENV \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # poetry:
  POETRY_HOME=/opt/poetry \
  POETRY_VERSION=1.4.2 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Install poetry as per official guidance:
# https://github.com/python-poetry/poetry#installation
RUN curl -sSL "https://install.python-poetry.org" | python -

# Add poetry's bin directory to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Copy files used by poetry
COPY pyproject.toml poetry.lock ./

# Copy application code
COPY . .

# Load shortcuts
RUN cp ./bash/bashrc.sh /root/.bashrc

# Install Python dependencies AND the 'etna' app
RUN poetry install

# Do nothing forever (use 'exec' to resuse the container)
CMD tail -f /dev/null
