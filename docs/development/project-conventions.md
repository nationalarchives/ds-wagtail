# Project conventions

At TNA we follow a set of conventions for our projects to ensure consistency and quality across our codebases. These can be found in our [developer handbook](https://nationalarchives.github.io/developer-handbook/) and should be followed when contributing to the Etna project, as well as the guidance below.

## Formatting

```sh
# Format and lint all Python, JavaScript, CSS, JSON etc.
docker compose exec dev format
```

## Migrations

We also have CI to check Django migrations, in order to help prevent any potential data issues. The CI will only run on a pull request, if any `/migrations` folders have been changed.

If a migration contains a potentially dangerous operation, the developer should check that the migration is safe to run, and verify they have checked this by adding a comment to the migration file,
in the following format:

```python
# etna:allowDeleteModel
```

The operations that require a comment are `DeleteModel`, `RenameModel`, `RemoveField`, and `AlterField`.

If the comment isn't added, the Github Action will flag that the migration is potentially dangerous, and the pull request will fail. The Github Action's log will tell you which file(s) are failing. The developer will then need to add the comment/check the migration, and push the changes to the pull request.

While this won't entirely stop potential data issues, it will help to catch any potential issues by forcing the developer to check that their migrations are sound, before they
are deployed.
