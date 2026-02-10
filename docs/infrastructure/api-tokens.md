# API tokens

Use the `manage_api_token` management command to create, refresh, or delete API tokens used by the API auth flow.

## Create a token

Create a new token (or show the existing key if it already exists):

```sh
manage manage_api_token my-service-name
```

## Refresh a token

Refresh an existing token (or create it if it does not exist):

```sh
manage manage_api_token my-service-name --refresh
```

## Delete a token

Delete a token by name or by key:

```sh
manage manage_api_token my-service-name --delete
manage manage_api_token 01234567-89ab-cdef-0123-456789abcdef --delete
```

## Notes

- The `identifier` argument accepts either the token name or token key when deleting.
- The command prints the API key when creating or refreshing a token. Avoid sharing it in public logs.
