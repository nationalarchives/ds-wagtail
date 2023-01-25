Related ticket(s):
- <- Paste ticket URL here ->

## About these changes

<- Add human-readable description here ->

## How to check these changes

<- Where possible, provide guidance to help your reviewer ->

## Before assigning to reviewer, please make sure you have

- [ ] Checked things thoroughly before handing over to reviewer.
- [ ] Checked PR title starts with ticket number as per project conventions to help us keep track of changes.
- [ ] Ensured that PR includes only commits relevant to the ticket.
- [ ] Waited for all CI jobs to pass before requesting a review.
- [ ] Added/updated tests and documentation where relevant.

## For Reviewer

- Before merging PR

    `main` branch :

        - check PR merge tile begins with `release/<major.minor.patch>:<default/custom description>`
        - check PR merge tile begins with ticket number Ex `DF-XXX: Ticket name / short description`
        - select `Create a merge commit`

    `develop` branch:

        - check if merges into base branch are `not to be kept On Hold` and then proceed.
        - check PR merge tile begins with ticket number Ex `DF-XXX: Ticket name / short description`
        - select `Squash and merge`

## For Reviewer/Developer

- After merging PR:

  - check and arrange to deploy on platform-sh.
  - update status on JIRA ticket on deployment.
  - update slack on deployment progress of the JIRA ticket once deployed.
