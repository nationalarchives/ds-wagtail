# Scheduled tasks

We normally write and execute scheduled tasks with [Django management commands](https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/), which are executed on the command line.

## The tasks

- `django-admin publish_scheduled_pages` - every 10 minutes or more often. This is necessary to make publishing scheduled pages work.
- `django-admin clearsessions` - once a day (not necessary, but useful).
- `django-admin update_index` - once a day (not necessary, but useful to make sure the search index stays intact).
