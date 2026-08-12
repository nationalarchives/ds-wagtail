# Version control

## Branching model

We follow the [GitHub flow branching model](https://docs.github.com/en/get-started/using-github/github-flow)/[trunk-based development](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development).

- Features are developed in a branch off of `main` (e.g. `feature/EDEV-123-some-new-changes`)
- Pull requests are created to merge the changes from the feature branch back into `main`
- Pull requests are squashed and merged into `main`
- Branches are deleted after being merged
- Releases are created via GitHub Actions/GitHub Releases
- `main` should always be a clean, working version of the project - ready to release at any time

**See below for merging guidance**

## Naming branches

- Use only alphanumeric characters and hyphens where possible and avoid special characters.
- Branch names for ticketed new features should follow: `feature/JIRA-TICKET-NUMBER-with-short-description`
- Branch names for ticketed bug fixes should follow: `fix/JIRA-TICKET-NUMBER-with-short-description`
- For example:
  - `feature/EDEV-123-extra-squiggles`
  - `fix/ABC-999-image-viewer-error`

## Naming pull requests

- Pull requests for features and bug fixes should be titled: `JIRA-TICKET-NUMBER: short-description`
- Pull requests for housekeeping tasks or other unticketed work should be titled: `CHORE: short-description`
- For example:
  - `UN-123: Add extra squiggles`
  - `DF-999: Fix image viewer error`
  - `CHORE: Update documentation`

## Merging branches

**NOTE:** Where possible, a feature branch should be kept up-to-date with `main` by regularly merging `main` into the feature branch. This will help to prevent conflicts when merging the feature branch back into `main`, and ensure there are no inconsistencies.

**Please ensure that you are using Squash and Merge when merging pull requests into `main`.**
This keeps the commit history clean and easy to track.