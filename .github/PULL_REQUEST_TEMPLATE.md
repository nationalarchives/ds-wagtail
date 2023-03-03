Ticket URL: paste URL here

## About these changes

Add a human-readable description here

## How to check these changes

Where possible, provide guidance to help your reviewer

## Before assigning to reviewer, please make sure you have

- [ ] Checked things thoroughly before handing over to reviewer.
- [ ] Checked PR title starts with ticket number as per project conventions to help us keep track of changes.
- [ ] Ensured that PR includes only commits relevant to the ticket.
- [ ] Waited for all CI jobs to pass before requesting a review.
- [ ] Added/updated tests and documentation where relevant.

## Merging a feature or bug fix?

1. Use the `Squash and merge` option to keep the target branch's commit history nice and clean.
2. Where relevant, include the ticket number in commit title, e.g. `DF-XXX: Ticket name / short description`.
3. Once PR is merged, check and arrange to deploy on hosted environment.

## Merging a release branch?

1. Use the `Create a merge commit` option to preserve the original commit IDs.
2. Use the message format `release/<major.minor.patch>` when merging.

## Deployment guidance

1. Post to the appropriate Slack channel to check that it is okay to continue.
2. To start a deployment, push the relevant branch to the `platform` remote.
3. Update the appropriate Slack channel when the deployment is complete.
4. Update the status on the corresponding Jira ticket (where relevant).
