FROM ghcr.io/nationalarchives/tna-python-django:0.2.3

ENV NPM_BUILD_COMMAND=compile
ENV DJANGO_SETTINGS_MODULE=config.settings.production

HEALTHCHECK CMD curl --fail http://localhost:8080/healthcheck/ || exit 1

# Copy in the project dependency files and config
COPY --chown=app pyproject.toml poetry.lock ./
COPY --chown=app package.json package-lock.json .nvmrc webpack.config.js ./
COPY --chown=app sass sass
COPY --chown=app scripts scripts
COPY --chown=app config config
COPY --chown=app templates templates

# Install Python dependencies AND the 'etna' app
RUN tna-build

# Copy application code
COPY --chown=app . .

# Copy the assets from the @nationalarchives/frontend repository
RUN mkdir -p /app/templates/static/assets; \
  cp -R /app/node_modules/@nationalarchives/frontend/nationalarchives/assets/* /app/templates/static/assets

CMD ["tna-run", "config.wsgi:application"]
