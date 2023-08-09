FROM ghcr.io/nationalarchives/tna-python-django:latest

ENV NPM_BUILD_COMMAND=compile

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

CMD ["tna-run", "config.wsgi:application"]
# CMD ["poetry", "run", "python", "/app/manage.py", "runserver", "0.0.0.0:8000"]
# CMD [ "tail", "-f", "/dev/null" ]
