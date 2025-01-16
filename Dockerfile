ARG IMAGE=ghcr.io/nationalarchives/tna-python-django
ARG IMAGE_TAG=latest

FROM "$IMAGE":"$IMAGE_TAG"

# TODO: Remove NPM_BUILD_COMMAND once completely headless
ENV NPM_BUILD_COMMAND=compile
ARG BUILD_VERSION
ENV BUILD_VERSION="$BUILD_VERSION"

# Copy in the application code
COPY --chown=app . .

# Install dependencies
RUN tna-build

# Copy the assets from the @nationalarchives/frontend repository
# TODO: Remove once completely headless
RUN mkdir -p /app/templates/static/assets; \
  cp -R /app/node_modules/@nationalarchives/frontend/nationalarchives/assets/* /app/templates/static/assets; \
  poetry run python /app/manage.py collectstatic --no-input --clear

# Delete source files, tests and docs
# RUN rm -fR /app/src /app/test /app/docs

CMD ["tna-run", "config.wsgi:application"]
