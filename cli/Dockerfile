# closely follows platformsh-cli in enta and fab pull-<env>-data
# should be updated accordingly for  hosted env
# FROM pjcdawkins/platformsh-cli:latest
# LABEL maintainer="dan@numiko.com"
FROM alpine:latest

WORKDIR /app

# RUN apt-get update && \
#     apt-get upgrade -y && \
#     apt-get install -y openssh-server git libpopt0 rsync && \
#     rm -rf /var/lib/apt/lists/*

# enables images upload for local development; do nothing forever - exec commands elsewhere
CMD chmod -fR 777 media; tail -f /dev/null