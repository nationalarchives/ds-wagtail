# API tokens

Use the `manage_api_token` management command to create, refresh, or delete API tokens used by the API auth flow.

```sh
# Create a new token
manage manage_api_token my-service-name

# Refresh an existing token (or create it if it does not exist)
manage manage_api_token my-service-name --refresh

# Delete a token
manage manage_api_token my-service-name --delete
```

## Notes

- The command prints the API key when creating or refreshing a token. Avoid sharing it in public logs.
