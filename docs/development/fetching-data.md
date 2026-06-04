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

Set up the AWS CLI (ensuring you select `AdministratorAccess` when prompted) as described in: https://national-archives.atlassian.net/wiki/spaces/TW/pages/775028742/Local+development#AWS-CLI-setup

From the ds-wagtail folder log into AWS before pulling data like so: 

```sh
aws sso login

# Pull all data and media from the development server
./dev/pull
```

Note: 

- To pull only data run `./dev/pull-data` 

- To only pull media run `./dev/pull-media`
