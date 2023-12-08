# Workflow for etna-rosetta

# entna-rosetta Branch, Environment:
- etna-rosetta is branched off `ds-wagtail:develop`
- is a long running branch which contains changes made for ROSETTA API (develop contains changes for KONG API)
- it is also an environment which is branched off develop
- it will be merged into develop when KONG API is decommissioned to use, or for some other reason.
- brings in new changes from develop
- adds any specific changes for Rosetta
- a CD will initiate to deploy to `etna-rosetta` for any merges into `etna-rosetta`


# Syncing entna-rosetta with channges from develop

Option 1
- create a branch off `etna-rosetta` eg: chore/sync-ddmmyyy
- merge develop branch into chore/sync-ddmmyyy
- fix conflicts
- create PR into `etna-rosetta`

Option 2
- merge develop into `etna-rosetta`
- fix conflicts


# Feature changes/fixes for entna-rosetta

- create feature,fix ticket branches off `etna-rosetta`
- merge latest changes from `etna-rosetta` into the feature branch
- create PR into `etna-rosetta`
- test feature in a spare environment if available