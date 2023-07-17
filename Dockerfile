# Generate static assets (CSS and JavaScript)
FROM node:18.16 AS staticassets
WORKDIR /home
COPY package.json package-lock.json webpack.config.js ./
RUN npm install
COPY scripts ./scripts
COPY sass ./sass
RUN npm run compile





FROM python:3.11

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

# Install poetry
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL "https://install.python-poetry.org" | python -

# Add poetry's bin directory to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Copy files used by poetry
COPY pyproject.toml poetry.lock ./

# Install Python dependencies AND the 'etna' app
RUN poetry install

# Copy the executable
COPY bash/run.sh bash/run-dev.sh bash/
RUN chmod +x bash/run.sh bash/run-dev.sh

# Copy application code
COPY . .

# Copy static assets
COPY --from=staticassets /home/templates/static/css/dist/etna.css /home/templates/static/css/dist/etna.css.map templates/static/css/dist/
COPY --from=staticassets /home/templates/static/scripts templates/static/scripts

# Gather the static assets
RUN poetry run python manage.py collectstatic --no-input

CMD ["./bash/run.sh"]
