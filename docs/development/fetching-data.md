# Fetching data

## Load local DB from an SQL file (No AWS access needed)

Without AWS access you can load your db locally using a dump and the following command:

`./dev/local-db-restore dumps/[my-db-file].sql`

**NOTE:** When fetching data:

- any Django users you created locally before running the command will no longer exist
- a superuser whose credentials are defined in `docker-compose.yml` will be created

## Download from development with AWS

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

  Media is extracted into the case-sensitive Docker named volume
  `extracted_media`, then synced to the local `wagtail` S3 bucket, preserving
  directory prefixes. Host extraction under `dumps/extract/` is not used: on
  case-insensitive filesystems, names differing only by case overwrite each other.

  Failed requests are retried up to 10 attempts. If the command fails, rerun it:
  matching-sized uploads are skipped, and extraction is reused when the archive
  SHA-256 is unchanged. Changed archives are extracted afresh.

  A dry-run sync verifies file presence and sizes (not content checksums), streaming
  any pending uploads. Downloads and extracted files are removed only after
  successful verification; failures retain them for retry. Any old host extraction
  under `dumps/extract/` is left untouched.
