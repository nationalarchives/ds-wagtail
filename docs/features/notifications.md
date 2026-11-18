# Notifications (alerts)

Alerts are reusable notification banners managed in Wagtail and exposed through
the API. A page can have an alert of its own, inherit a cascading alert from an
ancestor, or have no alert.

## Managing alerts in Wagtail

Create alerts from the **Alerts** or **Themed Alerts** snippet area:

- **Alert** has an importance level: `low`, `medium`, or `high` - these are used by TNA.
- **Themed Alert** has a visual theme: `green`, `yellow`, or `red` - these are used by the UKGWA.

Both kinds of alert share these fields:

| Field | Purpose |
| --- | --- |
| Name | Internal label to help editors identify the snippet. |
| Title | Short banner heading. |
| Message | Rich-text banner content. |
| Publish | Enables the alert. Alerts are unpublished by default, so they can be prepared ahead of time. |
| Show on current and all child pages | Makes the alert cascade through the page tree. |
| Active from | Optional scheduled start time. |
| Active to | Optional expiry time - the alert is no longer active at this time. |

Attach a snippet to a page using the alert field in that page's **Settings**
panel. A cascading alert set on the Home page is used as the site's global
alert. For descendants, a cascading alert inherited from an ancestor takes
precedence over an alert set directly on the child page. Without an inherited
cascading alert, the page's own alert is used if it is active.

An alert is active only when it is published and the current time is at or after
its start time (if set) and before its expiry time (if set). Wagtail validation
does not allow a start time in the past, or a start time at or after the expiry
time.

## API

The global notifications endpoint is:

```text
/api/v2/globals/notifications/
```

It returns notifications for the default site's Home page:

```json
{
  "global_alert": {
    "title": "Important information",
    "message": "<p>Example notification message</p>",
    "alert_level": "high",
    "cascade": true,
    "uid": 1730000000000
  },
  "mourning_notice": null
}
```

`global_alert` is `null` unless the Home page resolves to a cascading alert.
`mourning_notice` is a separate notification type. The catalogue landing
endpoint (`/api/v2/catalogue/landing/`) also includes these two fields.

Page API responses expose a `global_alert` field for pages configured with an
alert mixin. It resolves the alert for that page using the inheritance rules
above. Standard alerts include `alert_level` - themed alerts include `theme`
instead. In either response, an unpublished, not-yet-active, or expired alert
serializes as `null`. The message is returned as expanded rich text.

When `WAGTAILAPI_AUTHENTICATION` is enabled, the global notifications and
catalogue endpoints require API-token authentication.