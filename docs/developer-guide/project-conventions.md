# Etna project conventions

## Git branching model

We follow a loose version of the [Git flow branching model](https://nvie.com/posts/a-successful-git-branching-model/).

- Changes are developed in feature branches and submitted as pull requests via Github
- Feature branches should always be based on: `main`
- Pull requests should always be merged to: `main`

### Naming feature branches

- Branch names for new features should start with: `feature/`.
- Branch names for ticketed bugs should start with: `fix/`.
- Branch names for housekeeping tasks or other unticketed work should start with: `chore/`
- Ticket numbers should be included in branch names wherever possible. For example:
    - `feature/df123-extra-squiggles`
    - `fix/df999-image-view-error`
- Stick with alphanumeric characters and hyphens where possible and avoid random special characters.

## Submitting code changes

General advice:

- Submit pull-requests sooner rather than later: CI feedback is your friend, not your enemy
- Mark in-progress PRs as drafts until they are ready for review.
- Don't be afraid to show your working. We're all learning. If you need help, linking to code changes in a PR is a quick and easy way to explain the problem.

### Steps for submitting a pull request

1. Push your branch to the remote.
2. Head to https://github.com/nationalarchives/ds-wagtail/pulls and create a pull request from your branch.
    - For ticketed features of bug fixes, use the naming convention: `DF-XXX: Ticket name`.
    - For other fixes use the convention: `Fix: Short description`.
    - For housekeeping tasks or other unticketed work, use the convention: `Chore: Short description`.
3. To mark a PR as a draft, look for the **"Convert to draft"** link (after submitting) and click on it.
4. When you are finished (and CI is passing): Add a useful description, mark the PR as "Ready to review", and request a review from another developer.

## Deployment Cycle

TBC
