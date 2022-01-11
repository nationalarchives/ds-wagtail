FROM pjcdawkins/platformsh-cli:latest
LABEL maintainer="dan@numiko.com"

WORKDIR /app

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y openssh-server git libpopt0 rsync && \
    rm -rf /var/lib/apt/lists/*

# do nothing forever - exec commands elsewhere
CMD tail -f /dev/null
