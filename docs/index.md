# Etna Technical Documentation

## Project overview

- A brief summary of the project
- Who are the target audiences?
- What technologies are being used?

For help setting up a development environment, [view the README](https://github.com/nationalarchives/ds-wagtail/blob/main/README.md).

### External integrations

List here any key external services this project depends. Preferably link to a separate documentation page for each.

- [Search and record data (Client API)](features/search-and-record-data.md)

## Updating this documentation

The navigation for this this documentation is configured in [`mkdocs.yml`](https://github.com/nationalarchives/ds-wagtail/blob/main/). You can add new markdown files there to get them to appear in the navigation.

You can preview changes locally via [mkdocs](https://www.mkdocs.org/) by running the following from a `web` container shell:

```console
$ mkdocs serve
```

This will make your local copy of the documentation available in your browser at:
http://localhost:8001/

IMPORTANT: Remember that this documentation is public. Treat any sensitive data or credentials with the same level of caution that you would on any public forum.
