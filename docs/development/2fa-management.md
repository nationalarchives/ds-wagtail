# Two-Factor Authentication (2FA) management commands

## Commands

### `manage_2fa_devices`

- **Purpose**: Reset a user's account in a security-conscious way: remove 2FA devices, optionally reset recovery codes, revoke active sessions, reset the password, and send a password-reset notification email. Dry runs by default.

- **Location**: `app/api/management/commands/manage_2fa_devices.py`

Arguments and flags

- `--target-email <email>` (required): the user's email address.
- `--execute`: perform the destructive actions. Without `--execute` the command runs as a dry-run and prints what would be done.
- `--only-reset-recovery-codes`: when used together with `--execute`, delete _only_ the user's `StaticDevice` objects (these store single-use recovery codes). If omitted, `--execute` will remove all 2FA devices (TOTP and Static).
- `--reason "text"`: optional freeform reason to include in the notification email.

Example usages

- Dry-run (no changes):

```sh
manage_2fa_devices --target-email user@example.com
```

-- Execute reset of all 2FA devices, sessions, and password reset email (this will remove both TOTP and static recovery devices unless you pass the restriction flag):

```sh
manage_2fa_devices --target-email user@example.com --execute
```

-- Execute and only remove static recovery codes (so the middleware will recreate them at the user's next verified login):

```sh
manage_2fa_devices --target-email user@example.com --execute --only-reset-recovery-codes
```

Behavior notes

- When `--only-reset-recovery-codes` is used, only `StaticDevice` objects (the static recovery-code devices) are removed. Without this flag, `--execute` will remove all 2FA device types (TOTP and Static).
- Removing static devices is destructive: existing recovery codes are permanently removed. In this project the middleware will create a new `StaticDevice` and fresh recovery codes for a verified user on their next GET, and those codes will be displayed exactly once.
- Use `--execute` with care; the command sends a password reset email to the user when executed.

## Developer notes

- The underlying device creation logic is implemented in a small helper: `app/api/utils/twofa.py::create_static_device_with_tokens`. This is used by the onboarding middleware and was introduced to avoid code duplication.
- The old `generate_2fa_recovery_codes` management command has been removed; regeneration of recovery codes is now performed via `manage_2fa_devices --only-reset-recovery-codes` (or by calling the helper directly from a script).

## Testing

- To run the command locally in a dev environment use the project's `manage` helper, e.g.:

```sh
manage manage_2fa_devices --target-email user@example.com
```

- To run the full test suite (recommended after making changes):

```sh
docker-compose exec app poetry run pytest -q
```

## Safety checklist

- Confirm the target user email before running `--execute`.
- Prefer dry-run first.
- When removing `StaticDevice` objects communicate to the user that they will be shown new recovery codes only when they next sign in to the admin and that they must save them immediately.

## Dry-run examples

When you run the command without `--execute` it performs a dry run and prints what it would change.

- Inspect all device types (default):

```sh
manage manage_2fa_devices --target-email user@example.com
```

Sample output (dry run):

```
--- Step 2: Remove 2FA Devices ---
Found 3 device(s) to remove:
	- TOTP: Primary authenticator (ID: 12)
	- TOTP: Backup authenticator (ID: 13)
	- Recovery codes: Recovery codes (ID: 14)
DRY RUN: would delete 3 2FA device(s).
```

- Inspect only recovery codes (use `--only-reset-recovery-codes`):

```sh
manage manage_2fa_devices --target-email user@example.com --only-reset-recovery-codes
```

Sample output (dry run):

```
--- Step 2: Remove 2FA Devices ---
Found 1 device(s) to remove:
	- Recovery codes: Recovery codes (ID: 14)
DRY RUN: would delete 1 StaticDevice(s).
```
