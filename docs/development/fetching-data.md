# Fetching data

## Prerequisites

The following steps must be completed before you can pull data from an evironment:

1. [Register for a Platform.sh account](https://auth.api.platform.sh/register) using your work email
2. On the `#ds-etna` or `#ds-etna-dev` Slack channels, request for someone to add you to the Etna project
3. Once you have access, [generate an API token](https://docs.platform.sh/development/cli/api-tokens.html#get-a-token) for your account (The name **Local CLI** will do nicely), and add it your local `.env` file as `PLATFORMSH_CLI_TOKEN`

Developers from external agencies may not be able to register for a platform.sh account. In this scenario, ask a developer from The National Archives to share their API key.

**NOTE:** When fetching data:

- any Django users you created locally before running the command will no longer exist
- a superuser whose credentials are defined in `docker-compose.yml` will be created

## Download from development

```sh
# Pull all data and media from the development server
docker compose exec dev pull

# Pull just the data from the development server
docker compose exec dev pull-data

# Pull just the media from the development server
docker compose exec dev pull-media
```

### Download from production

```sh
# Pull all data and media from the production server
docker compose exec dev pull main

# Pull just the data from the production server
docker compose exec dev pull-data main

# Pull just the media from the production server
docker compose exec dev pull-media main
```
