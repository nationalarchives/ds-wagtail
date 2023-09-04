# Fetching data

Fetch data from hosted environments.

- The production data is pulled from the `main` environment.
- The staging data is pulled from the `develop` environment.

## Prerequisites

The following steps must be completed before you can pull data from an evironment:

1. [Register for a Platform.sh account](https://auth.api.platform.sh/register) using your work email.
2. On the `#ds-etna` or `#ds-etna-dev` Slack channels, request for someone to add you to the Etna project.
3. Once you have access, [generate an API token](https://docs.platform.sh/development/cli/api-tokens.html#get-a-token) for your account (The name **Local CLI** will do nicely), and add it your local `.env` file as `PLATFORMSH_CLI_TOKEN`.

## Download environment data

Run the following command from the console. NOTE: This will not work from within an existing shell session, so you may have to exit that first.

### Staging

```console
$ fab pull-staging-data
```

### Production

```console
$ fab pull-production-data
```

**NOTE:** Data is automatically anonymised after downloading to protect sensitive data, so user logins from production will NOT work locally. Also, any Django users you created locally before running the command will no longer exist. You can run `python manage.py createsuperuser` from a container shell to create yourself a new one.

## Download environment media

Run the following command from the console. NOTE: This will not work from within an existing shell session, so you may have to exit that first.

**N.B. These commands must be run with `sudo` so the permissions can be correctly updated once pulled. This is to fix an issue which will be resolved once we move platforms.**

### Staging

```console
$ sudo fab pull-staging-media
```

### Production

```console
$ sudo fab pull-production-media
```