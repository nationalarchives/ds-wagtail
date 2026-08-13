# Environments

## Deploying to an environment

### Deploying to develop

Any code that is merged into the `main` branch will be automatically deployed to the `develop` environment. A merge to `main` triggers the `update-ds-infrastructure-web` Action, which updates the [develop.json config](https://github.com/nationalarchives/ds-infrastructure-web/blob/main/config/develop.json) in [`ds-infrastructure-web`](https://github.com/nationalarchives/ds-infrastructure-web). Further Actions are run on `ds-infrastructure-web` - please see the [`ds-infrastructure-web` repo](https://github.com/nationalarchives/ds-infrastructure-web) for more information.

### Deploying to staging and production

**Both `staging` and `production` are managed via [`ds-infrastructure-web`](https://github.com/nationalarchives/ds-infrastructure-web). This information may not be up-to-date with current workflows for deploying to either environment.**

#### Staging

Run the [Release to staging](https://github.com/nationalarchives/ds-infrastructure-web/actions/workflows/deploy-staging.yml) Action on the `ds-infrastructure-web` repo. This will update all applications on `staging` with the latest versions that are on `develop`.

#### Production

After the `Release to staging` Action has finished running, a draft release will be available in the [Releases tab](https://github.com/nationalarchives/ds-infrastructure-web/releases) of `ds-infrastructure-web`. Publish this, and have a colleague approve the Action.

## Adding/updating environment variables

Some changes may require environment variables to be added or updated. These should be edited in the relevant [`config/parameters/wagtail`](https://github.com/nationalarchives/ds-infrastructure-web/tree/main/config/parameters/wagtail) file. There is a `json` file for each environment. Further information can be found in [Environment variables](../env-vars.md).

## Manual deployments to a specific environment

Each PR runs the `build` action which creates a [tagged image version](https://github.com/nationalarchives/ds-wagtail/pkgs/container/ds-wagtail) of your branch. This tag can then be used with the [`Deploy single application`](https://github.com/nationalarchives/ds-infrastructure-web/actions/workflows/deploy-specific-application-version.yml) Action to deploy to either `develop` or `staging` without needing to merge to `main` or create a release. This allows us to test features before merging them.

**Do not deploy a branch/version that includes migrations.** This will affect the database of the selected environment, and will require a rollback/backup to fix. If you must do this, speak with Platform Team colleagues first to organise this safely.

If any of the above fails, or you have concerns or questions, please contact a Platform Team colleague.
