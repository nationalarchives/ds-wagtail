ARG IMAGE=ghcr.io/nationalarchives/tna-python
ARG IMAGE_TAG=latest

FROM "$IMAGE":"$IMAGE_TAG"

ARG BUILD_VERSION
ENV BUILD_VERSION="$BUILD_VERSION"
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Copy in the application code
COPY --chown=app . .

# Install dependencies
RUN tna-build

# Collect static files
RUN poetry run python /app/manage.py collectstatic --no-input --clear

# Clean up build dependencies
RUN tna-clean

CMD ["tna-wsgi", "config.wsgi:application"]
