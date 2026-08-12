# Backend development

Specific guidance for working on on backend tasks.

## Running Django management commands

All Django commands should be run in the `app` container.

To run a command, run:

```sh
docker compose exec app poetry run ...
```

With this, you can interact with Django exactly as you can see outlined in [the official documentation](https://docs.djangoproject.com/en/stable/topics/migrations/#module-django.db.migrations) and the many tutorials you'll find on the web.

For example, to make migrations:

```sh
docker compose exec app poetry run python manage.py makemigrations
```

It may be beneficial to create an alias for these commands, e.g. `docker compose exec app` becomes `dcea`, or `docker compose exec app poetry run` becomes `dceap`. This is not necessary, but can save time.

## Common Django management commands

Below are some commands you'll use regularly:

### Generating database migrations

To make migrations for a new app:

```sh
... manage.py makemigrations
```

To make migrations for an existing app, use the `-n` argument to provide a meaninful name to help your peers understand what the migration does:

```sh
... manage.py makemigrations [appname] -n meaningful_name_here
```

### Applying database migrations

To apply migrations for all apps:

```sh
... manage.py migrate
```

To apply migrations for a specific app:

```sh
... manage.py migrate [appname]
```

### Reversing database migrations

To reverse migrations for an app, specify the number of the migration you want to **revert back to**. For example, if you wanted to reverse the following migrations:

- `003_add_cat_gif_image_field`
- `004_tweak_streamfield_options`
- `005_add_fks_to_insights_pages`

You would run:

```sh
... manage.py  migrate [appname] 002
```

If you need to reverse ALL migrations for an app, use the 'zero' keyword, like so:

```sh
... manage.py  migrate [appname] zero
```

### Writing custom migrations

Use a custom migration when schema changes are not enough on their own, for example when you need to:

- backfill data after adding a field
- move from one data-type to another, e.g. `str` to `int`
- run database-specific SQL

Custom migrations should be:

- **small** (one clear job)
- **reversible** where possible
- **safe to run more than once** (idempotent)

#### 1. Generate a new empty migration

Create an empty migration file for your app:

```sh
... manage.py makemigrations [appname] --empty -n describe_the_change
```

This creates a migration where you can add custom operations.

#### 2. Choose the right operation type

Common options:

- `migrations.RunPython` for data migrations in Python
- `migrations.RunSQL` for raw SQL migrations
- built-in operations like `AddField`, `AlterField`, `AlterModelOptions` for schema changes

Often, a migration mixes schema and data operations in sequence.

#### 3. Example: data backfill with `RunPython`

```python
# app/[appname]/migrations/00xx_backfill_slug.py
from django.db import migrations


def forwards(apps, schema_editor):
	ArticlePage = apps.get_model("articles", "ArticlePage")

	for page in ArticlePage.objects.filter(slug=""):
		page.slug = f"article-{page.pk}"
		page.save(update_fields=["slug"])


def backwards(apps, schema_editor):
	ArticlePage = apps.get_model("articles", "ArticlePage")
	ArticlePage.objects.filter(slug__startswith="article-").update(slug="")


class Migration(migrations.Migration):
	dependencies = [
		("articles", "00xx_previous_migration"),
	]

	operations = [
		migrations.RunPython(forwards, backwards),
	]
```

Key points:

- Use `apps.get_model(...)` inside migrations, not direct imports from `models.py`.
- Keep queries targeted (`filter(...)`) to avoid full-table updates when unnecessary.
- Provide a reverse function where practical.

#### 4. Example: SQL migration with `RunSQL`

```python
from django.db import migrations


class Migration(migrations.Migration):
	dependencies = [
		("api", "00xx_previous_migration"),
	]

	operations = [
		migrations.RunSQL(
			sql="CREATE INDEX CONCURRENTLY IF NOT EXISTS api_model_field_idx ON api_model (field);",
			reverse_sql="DROP INDEX IF EXISTS api_model_field_idx;",
		),
	]
```

If SQL is not reversible, use:

```python
migrations.RunSQL(sql="...", reverse_sql=migrations.RunSQL.noop)
```

#### 5. Test your migration flow

Before opening a PR:

1. Run forward migrations from a clean state.
2. Run backwards for the target app (or specific migration) and verify reversibility.
3. Re-run forwards to ensure repeatability.

Useful commands:

```sh
... manage.py showmigrations [appname]
... manage.py migrate [appname] [migration_number]
... manage.py migrate [appname]
```

#### 6. Practical safeguards

- Avoid importing runtime code that may change in future; use migration-local helpers.
- Keep long-running transformations in batches for large tables.
- Add guards for existing/partial state when needed.
- Prefer separate migrations for: schema add -> data backfill -> constraint tighten.
- Add a comment/docstring to explain the need/use case for the custom migration.

This staged approach reduces downtime risk and makes rollback easier.
