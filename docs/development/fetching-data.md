# Fetching data

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

- To solely pull data run `./dev/pull-data`

- To solely pull media run `./dev/pull-media`
