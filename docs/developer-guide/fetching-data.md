# Fetching data

Fetch data from hosted environments.

- The production data is pulled from the `main` environment.
- The staging data is pulled from the `develop` environment.

## Prerequisites

The following steps must be completed before you can pull data from an evironment:

1. [Register for a Platform.sh account](https://auth.api.platform.sh/register) using your work email.
2. On the `#ds-etna` or `#ds-etna-dev` Slack channels, request for someone to add you to the Etna project.
3. Once you have access, [generate an API token](https://docs.platform.sh/development/cli/api-tokens.html#get-a-token) for your account (The name **Local CLI** will do nicely), and add it your local `.env` file as `PLATFORMSH_CLI_TOKEN`.

Developers from external agencies may not be able to register for a platform.sh account. In this scenario, ask a developer from The National Archives to share their API key.

## Download environment data

### Staging

```sh
docker compose exec dev pull-data
```

### Production

```sh
docker compose exec dev pull-data main
```

**NOTE:**

- Data is automatically anonymised after downloading to protect sensitive data, so user logins from production will NOT work locally.
- Also, any Django users you created locally before running the command will no longer exist.
- A superuser whose credentials are defined in the docker-compose.yml will be created.

## Download environment media

### Staging

```sh
docker compose exec dev pull-media
```

### Production

```sh
docker compose exec dev pull-media main
```

## Download everything

### Staging

```sh
docker compose exec dev pull
```

### Production

```sh
docker compose exec dev pull main
```
