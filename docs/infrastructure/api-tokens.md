# API tokens

Use the `manage_api_token` and `list_api_tokens` management commands to create, refresh, or delete API tokens used by the API auth flow.

Run these commands in the `app` container:

```sh
# Create a new token
docker compose exec app poetry run python manage.py manage_api_token my-service-name

# Show an existing token
docker compose exec app poetry run python manage.py manage_api_token my-service-name --show

# Refresh an existing token (or create it if it does not exist)
docker compose exec app poetry run python manage.py manage_api_token my-service-name --refresh

# Delete a token
docker compose exec app poetry run python manage.py manage_api_token my-service-name --delete

# Disable a token
docker compose exec app poetry run python manage.py manage_api_token my-service-name --disable

# Enable a token
docker compose exec app poetry run python manage.py manage_api_token my-service-name --enable

# List existing tokens
docker compose exec app poetry run python manage.py list_api_tokens
```

## Notes

- The command prints the API key when creating or refreshing a token. Avoid sharing it in public logs.
