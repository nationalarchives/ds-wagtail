# Generate static assets (CSS and JavaScript)
FROM node:20.5 AS staticassets
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
  POETRY_HOME=/home/app/poetry \
  POETRY_VERSION=1.4.2 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=true

# Create the non-root user and the application directory
RUN useradd --system --create-home app && \
    mkdir -p /app && \
    chown app:app -R /app && \
    chmod 700 /app
WORKDIR /app
USER app

# Install poetry
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL "https://install.python-poetry.org" | python -

# Add poetry's bin directory to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Copy files used by poetry
COPY --chown=app pyproject.toml poetry.lock ./

# Install Python dependencies AND the 'etna' app
RUN poetry install

# Copy application code
COPY --chown=app . .
RUN chmod +x /app/bash/run.sh

# Copy static assets
COPY --chown=app --from=staticassets /home/templates/static/css/dist/etna.css /home/templates/static/css/dist/etna.css.map templates/static/css/dist/
COPY --chown=app --from=staticassets /home/templates/static/scripts templates/static/scripts

# Gather the static assets
RUN poetry run python manage.py collectstatic --no-input

CMD ["/app/bash/run.sh"]
