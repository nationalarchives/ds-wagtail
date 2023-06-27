# Hosted environments

## List of environments in use and the branches to which they are tied

The GitHub branch and Hosted environments have the same name:

- `main`: for Live/Production
- `develop`: for Development


## Pre-requisites for deployment to develop

1. If your new code requires any Platform.sh environment variables to either be updated or created, please speak to someone who has access to the Platform.sh environment before deploying/merging your code.
- The new variables should follow the naming convention as the other variables, which is `env:VARIABLE_NAME`

## Deploying to develop

We now have CD (Continuous Delivery) actions set up on Github.
This now allows us to run automated deployments when code is merged to `develop`.

**Please ensure that you are using Squash and Merge when merging pull requests into `develop`.**
This keeps the commit history clean and easy to track.

When your code has been merged, the action will start. Once completed, a notification will be sent in the Slack channel `ds-platform-sh-notifications`.
Your code will then be visible on the `develop` environment.

Provided that you have used the correct naming conventions for your branch and PR, the JIRA ticket associated with your branch will be updated and moved into the `READY TO TEST ON DEVELOP` swim lane.
Otherwise, you will need to manually move the ticket into the `READY TO TEST ON DEVELOP` swim lane.


## Pre-requisites for deployment to main

1. If your new code requires any Platform.sh environment variables to either be updated or created, please speak to someone who has access to the Platform.sh environment before deploying/merging your code.
- The new variables should follow the naming convention as the other variables, which is `env:VARIABLE_NAME`
2. A branch must be created from `develop`, you should call this `release/X.X.X`, with the `X`s being relative to the major, minor, and patch level of the release.
3. A pull request should be created to merge `release/X.X.X` into `main`, titled `Release X.X.X into main`.
4. The pull request should contain a summary of all commits since the last release.
- This can be obtained by running `git log --oneline` for a shortened version of the commit history.
5. Create a "release" on [Github releases](https://github.com/nationalarchives/ds-wagtail/releases)
- Create a new tag to match your release number, and title it `Release X.X.X`

## Deploying to main

We now have CD (Continuous Delivery) actions set up on Github.
This now allows us to run automated deployments when code is merged to `main`.

!!! Please ensure that you are using Merge Commit when merging releases into `main`.
This brings all the commits from the release branch into `main` to keep the commit history continuous from `develop`.

When your code has been merged, the action will start. Once completed, a notification will be sent in the Slack channel `#ds-platform-sh-notifications`.
Your code will then be visible on the `main` environment.

After merging into `main`, make a pull request to merge `main` into `develop`.
This will ensure that `develop` includes the commit from `main` and will prevent any conflicts when merging future releases into `main` to keep the history in sync.

Provided that you have used the correct naming conventions for your branch and PR, the JIRA ticket associated with your branch will be updated and moved into the `READY TO TEST ON MAIN` swim lane.
Otherwise, you will need to manually move the deployed tickets into the `READY TO TEST ON MAIN` swim lane.

Please then update the `#ds-etna-dev` Slack channel and let the team know that `develop` is free to be used again.


## Manual deployments to environments

If CD fails for any reason and cannot be fixed, you can manually deploy to an environment by following the steps below:

```console
platform project:set-remote <project_id>
```

# Develop
```console
git push platform develop
```

# Main
```console
git push platform main
```

## How to access the Platform.sh shell

1. Go to the Platform.sh dashboard
2. Click on the environment you want to access
3. Click on the `SSH` tab
4. Copy the SSH command
5. Open your `ds-wagtail-cli1` container in Docker Desktop
6. Paste the command into the CLI
7. You should now be in the Platform.sh shell