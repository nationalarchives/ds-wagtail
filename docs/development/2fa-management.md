# Two-Factor Authentication (2FA) management commands

## Commands

### `manage_2fa_devices`

- **Purpose**: Reset a user's account in a security-conscious way: remove all 2FA devices (revoke active sessions, reset the password, and send a password-reset notification email), or only reset recovery codes. Dry runs by default.

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

-- Execute reset of all 2FA devices, sessions, and password (this will remove _both_ TOTP and static recovery devices unless you pass `--only-reset-recovery-codes`):

```sh
manage_2fa_devices --target-email user@example.com --execute
```

-- Execute and only remove static recovery codes (so the middleware will recreate them at the user's next verified login):

```sh
manage_2fa_devices --target-email user@example.com --execute --only-reset-recovery-codes
```

-- List users without any 2FA devices (use the dedicated list_2fa_devices command):

```sh
list_2fa_devices --missing-2fa
```

-- List users who have 2FA configured but lack recovery codes (use the dedicated list_2fa_devices command):

```sh
list_2fa_devices --missing-recovery-codes
```

Behavior notes

- Dry-runs by default (email template dry-run has been removeed and replaced with the proposed subject and reason, if included.)
- When `--only-reset-recovery-codes` is used, only `StaticDevice` objects (the static recovery-code devices) are removed. Without this flag, `--execute` will remove all 2FA device types (TOTP and Static).
- The list flags do not require `--target-email` and will exit after printing matches.
- The list command `list_2fa_devices` does not require `--target-email` and will exit after printing matches.
- Removing static devices is destructive: existing recovery codes are permanently removed. The middleware will create a new `StaticDevice` and fresh recovery codes for a verified user on their next GET, and those codes will be displayed exactly once.

## Safety checklist

- Confirm the target user email before running `--execute`.
- Prefer dry-run first.
- When resetting recovery codes communicate with emphasis to the user that they will be shown new recovery codes only when they next sign in to the admin and that they must save them immediately.
