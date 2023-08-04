# Generate static assets (CSS and JavaScript)
FROM node:18.16 AS staticassets
WORKDIR /home
COPY package.json package-lock.json webpack.config.js ./
RUN npm install
COPY scripts ./scripts
COPY sass ./sass
RUN npm run compile





FROM ghcr.io/nationalarchives/tna-python:main

# Copy files used by poetry
COPY --chown=app pyproject.toml poetry.lock ./

# Install Python dependencies AND the 'etna' app
RUN tna-build

# Copy application code
COPY --chown=app . .
RUN chmod +x /app/bash/run.sh

# Copy static assets
COPY --chown=app --from=staticassets /home/templates/static/css/dist/etna.css /home/templates/static/css/dist/etna.css.map templates/static/css/dist/
COPY --chown=app --from=staticassets /home/templates/static/scripts templates/static/scripts

# Gather the static assets
RUN poetry run python manage.py collectstatic --no-input

CMD ["/app/bash/run.sh"]
