FROM ghcr.io/nationalarchives/tna-python-django:latest

COPY --chown=app dev/bin /home/app/.local/bin/dev
RUN chmod +x -fR /home/app/.local/bin/dev
ENV PATH="/home/app/.local/bin/dev:$PATH"

COPY --chown=app pyproject.toml poetry.lock ./
RUN poetry install

COPY --chown=app .nvmrc .nvmrc
RUN setup-npm

COPY --chown=app . .

USER root

CMD ["tail", "-f", "/dev/null"]
