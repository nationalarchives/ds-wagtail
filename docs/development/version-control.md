# Version control

## Branching model

We follow a loose version of the [Git flow branching model](https://nvie.com/posts/a-successful-git-branching-model/).

- Changes are developed in feature branches and submitted as pull requests via Github
- Feature branches should always be based on: `develop`
- Release branches should always be based on: `develop`
- Release branches should be merged via PR into `main`, followed by PR to merge `main` into `develop`
- Create a new branch if the branch for that ticket has been merged.

**See below for merging guidance**

## Naming branches

- Use only alphanumeric characters and hyphens where possible and avoid special characters.
- Branch names for ticketed new features should follow: `feature/JIRA-TICKET-NUMBER-with-short-description`
- Branch names for ticketed bug fixes should follow: `fix/JIRA-TICKET-NUMBER-with-short-description`
- Branch names for releases should follow: `release/major.minor.patch`
- Branch names for housekeeping tasks or other unticketed work should follow: `chore/short-description`
- For example:
  - `feature/UN-123-extra-squiggles`
  - `fix/DF-999-image-view-error`
  - `release/1.0.0`
  - `chore/update-documentation`

## Naming pull requests

- Pull requests for features and bug fixes should be titled: `JIRA-TICKET-NUMBER: short-description`
- Pull requests for release branches should be titled: `Release X.X.X into main`
- Pull requests for housekeeping tasks or other unticketed work should be titled: `CHORE: short-description`
- For example:
  - `UN-123: Add extra squiggles`
  - `DF-999: Fix image view error`
  - `Release 1.0.0 into main`
  - `CHORE: Update documentation`

## Merging branches

**NOTE:** Where possible, a feature branch should be kept up-to-date with `develop` by regularly merging `develop` into the feature branch. This will help to prevent conflicts when merging the feature branch back into `develop`, and ensure there are no inconsistencies.

- When merging a feature branch into `develop`, use the `Squash and merge` option to keep the commit history clean
- When merging a release branch into `main`, use the `Merge commit` option to keep the commit history continuous from `develop`
- When merging `main` back into `develop` (after merging a release branch into `main`), use the `Merge commit` option to prevent any conflicts when merging future releases into `main` to keep the history in sync
  - This should be named `Release X.X.X main into develop` to make it clear what the merge is for
