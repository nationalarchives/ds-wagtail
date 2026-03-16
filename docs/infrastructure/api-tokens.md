# API tokens

Use the `manage_api_token` and `list_api_tokens` management commands to create, refresh, or delete API tokens used by the API auth flow.

```sh
# Create a new token
poetry run python manage.py manage_api_token my-service-name

# Show an existing token
poetry run python manage.py manage_api_token my-service-name --show

# Refresh an existing token (or create it if it does not exist)
poetry run python manage.py manage_api_token my-service-name --refresh

# Delete a token
poetry run python manage.py manage_api_token my-service-name --delete

# Disable a token
poetry run python manage.py manage_api_token my-service-name --disable

# Enable a token
poetry run python manage.py manage_api_token my-service-name --enable

# List existing tokens
poetry run python manage.py list_api_tokens
```

## Notes

- The command prints the API key when creating or refreshing a token. Avoid sharing it in public logs.
