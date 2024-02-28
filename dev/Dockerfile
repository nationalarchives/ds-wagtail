FROM ghcr.io/nationalarchives/tna-python-django:0.2.3

USER root

RUN apt-get update; \
  apt-get install -y ca-certificates curl gnupg; \
  install -m 0755 -d /etc/apt/keyrings; \
  curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg; \
  chmod a+r /etc/apt/keyrings/docker.gpg; \
  echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null; \
  apt-get update; \
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

COPY --chown=app dev/bin /home/app/.local/bin/dev
RUN chmod +x -fR /home/app/.local/bin/dev
ENV PATH="/home/app/.local/bin/dev:$PATH"

COPY --chown=app pyproject.toml poetry.lock ./
RUN poetry install

COPY --chown=app .nvmrc .nvmrc
RUN setup-npm

COPY --chown=app . .

CMD ["welcome"]
