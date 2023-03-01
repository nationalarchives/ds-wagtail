# Hosted environments

## List of environments in use and the branches to which they are tied

The GitHub branch and Hosted environments have the same name:

- `main`: for Live/Production
- `develop` : for Development

## How deployments are triggered

- Deployments are manual at this time.

### Pre-requisites

- Requires user access on the hosted environment for deployments. Check with management if you need one.
- Follow Branching Model and Naming branches [docs\developer-guide\project-conventions.md] (https://nationalarchives.github.io/ds-wagtail/developer-guide/project-conventions/)
- Check if it is Ok to deploy see guidance on deployment [.github\PULL_REQUEST_TEMPLATE.md](https://github.com/nationalarchives/ds-wagtail/blob/develop/.github/PULL_REQUEST_TEMPLATE.md)
- Test on local before deploy to environment

### main

#### Set environment variables from the UI console for `main` environment

- env:MAINTENANCE_MODE=True
- env:MAINTENENCE_MODE_ALLOW_IPS='< ip >'
- any others as required (for `main` environment or at project level)

#### Deploy to the environment

```console
platform project:set-remote <project_id>
```

```console
git push platform main
```

#### Run a check from the IP to see if the site works

#### Reset environment variables from the UI console

- env:MAINTENANCE_MODE=False
- env:MAINTENENCE_MODE_ALLOW_IPS (Remove)
- any others as required

#### Convey the deployment is completed

### develop

#### Set environment variables from the UI console for `develop` environment

- set as required

#### Deploy

```console
platform project:set-remote <project_id>
```

```console
git push platform develop
```

#### Convey the deployment is completed

## General advice: Trust the pipeline and deploy small changes regularly

## How to access a shell

## How to pull data (link to developer-guide/fetching-production-data.md)
