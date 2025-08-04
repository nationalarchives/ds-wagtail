ARG IMAGE=ghcr.io/nationalarchives/tna-python-django
ARG IMAGE_TAG=latest

FROM "$IMAGE":"$IMAGE_TAG"

ARG BUILD_VERSION
ENV BUILD_VERSION="$BUILD_VERSION"
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Copy in the application code
COPY --chown=app . .

# Install dependencies
RUN tna-build

CMD ["tna-run", "config.wsgi:application"]
