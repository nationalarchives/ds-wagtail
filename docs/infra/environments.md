# Hosted environments

## List of environments in use and the branches to which they are tied

The GitHub branch and Hosted environments have the same name:

- `main`: for Live/Production
- `develop` : for Development

## How deployments are triggered

- Deployments are manual

## Pre-requisites for deployment

- Requires user access on the hosted environment for deployments. Check with management if you need one.
- Follow Branching Model and Naming branches [project-conventions](https://nationalarchives.github.io/ds-wagtail/developer-guide/project-conventions/)
- Post to the appropriate Slack channel to check that it is okay to continue.
- Test on local before deploy to environment

## Deploying to main

1. Set environment variables from the UI console for `main` environment

    - env:MAINTENANCE_MODE=True
    - env:MAINTENENCE_MODE_ALLOW_IPS='< ip >'
    - any others as required (for `main` environment or at project level)

2. Deploy to the environment

    ```console
    platform project:set-remote <project_id>
    ```

    ```console
    git push platform main
    ```

3. Run a check from the IP to see if the site works

4. Reset environment variables from the UI console

    - env:MAINTENANCE_MODE=False
    - env:MAINTENENCE_MODE_ALLOW_IPS (Remove)
    - any others as required

5. Update the appropriate Slack channel when the deployment is complete.

6. Update the status on the corresponding Jira ticket (where relevant).

## Deploying to develop

1. Set environment variables from the UI console for `develop` environment

    - set as required

2. Deploy to the environment

    ```console
    platform project:set-remote <project_id>
    ```

    ```console
    git push platform develop
    ```

3. Update the appropriate Slack channel when the deployment is complete.

4. Update the status on the corresponding Jira ticket (where relevant).

## General advice: Trust the pipeline and deploy small changes regularly

## How to access a shell

## How to pull data (link to developer-guide/fetching-production-data.md)
