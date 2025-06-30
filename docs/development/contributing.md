# Contributing code

Before contributing code, please familiarise yourself with the [Project conventions](project-conventions.md).

## General advice:

- Submit pull-requests sooner rather than later: CI feedback is your friend, not your enemy.
- Mark in-progress PRs as drafts until they are ready for review.
- Don't be afraid to show your working. We're all learning. If you need help, linking to code changes in a PR is a quick and easy way to explain the problem.
- Where possible, a feature branch should be kept up-to-date with `develop` by regularly merging `develop` into the feature branch. This will help to prevent conflicts when merging the feature branch back into `develop`, and ensure there are no inconsistencies.

## Submitting a pull request (PR)

1. Push your branch to the remote.
2. Head to https://github.com/nationalarchives/ds-wagtail/pulls and create a pull request from your branch.

   For the PR Title:
   - For ticketed features or ticketed bugs, use the naming convention: `DF-XXX: Short description`
   - For housekeeping tasks or other unticketed work, use the convention: `CHORE: Short description`

   See [here](project-conventions.md#naming-pull-requests) for more information on naming conventions.

3. To mark a PR as a draft, click the drop-down where it says **"Create pull request"** and select the **"Create draft pull request"** button instead.
4. When you are finished (and CI is passing): Add a useful description, mark the PR as "Ready to review", and request a review from another developer.

## Merging a branch?

Please see [here](project-conventions.md#merging-branches) for guidance on merging branches.
