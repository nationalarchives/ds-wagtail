# Release

1. Merge all code into `main`
1. Run the "Create release" workflow (https://github.com/nationalarchives/ds-wagtail/actions/workflows/create-release-tag.yml) against the `main` branch
    1. A pull request is created with the release number in calver format
    1. A release is drafted
    1. A tag is created
1. Merge the created pull request into `main` to update the release number
1. Publish the drafted release that was created on the [releases page](https://github.com/nationalarchives/ds-wagtail/releases)
1. A Docker image will be created
1. The site will be pushed to platform.sh
1. Pull the changes from `main` down to `develop`
