# Multi-Site Setup Guide

This project supports multiple Wagtail sites, allowing different departments to have separate content trees while sharing the same codebase and page types.

## Overview

As of the latest migration, this project includes:

- **Site 1 (Default)**: The National Archives main site - `localhost` (port 80) in production, `localhost:8000` in development
- **Site 2**: Second department site - `localhost:8001` in development

Each site has its own:

- Root HomePage
- Page tree (all pages are descendants of the root page)
- Global alerts and mourning notices
- Independent content managed through Wagtail admin

## Setup & Migration

### Running the Migration

The second site is created automatically via data migration when you run:

```bash
# Using Docker (recommended)
docker-compose exec app python manage.py migrate home

# Or locally
python3 manage.py migrate home
```

This will:

1. Remove the `max_count = 1` restriction from HomePage
2. Create a second HomePage at `/home-site-2/`
3. Create a Site object pointing to it with hostname `localhost:8001`

### Accessing Sites in Development

**Default site (Site 1):**

- Wagtail Admin: `http://localhost:8000/admin/`
- API: `http://localhost:8000/api/v2/`

**Second site (Site 2):**

- Access through admin, or
- API with site parameter: `http://localhost:8000/api/v2/pages/?site=localhost:8001`

## API Usage

### Site-Aware Endpoints

The following endpoints respect the `?site=` parameter and will default to the default site if not specified:

- `/api/v2/pages/` - All pages
- `/api/v2/events/` - Events
- `/api/v2/blog_posts/` - Blog posts
- `/api/v2/images/` - Images
- `/api/v2/media/` - Media
- `/api/v2/redirects/` - Redirects
- `/api/v2/globals/notifications/` - Global alerts and mourning notices
- `/api/v2/globals/navigation/` - Site-specific navigation settings

### Usage Examples

```bash
# Get pages from default site (Site 1)
GET /api/v2/pages/

# Get pages from second site (Site 2)
GET /api/v2/pages/?site=localhost:8001

# Get global notifications for default site
GET /api/v2/globals/notifications/

# Get global notifications for second site
GET /api/v2/globals/notifications/?site=localhost:8001

# Get navigation settings for default site
GET /api/v2/globals/navigation/

# Get navigation settings for second site
GET /api/v2/globals/navigation/?site=localhost:8001
```

### Navigation Settings

The `/api/v2/globals/navigation/` endpoint returns site-specific navigation configuration for use in headers and footers.

**Response structure:**

```json
{
  "primary_navigation": [],
  "secondary_navigation": [],
  "footer_navigation": [],
  "footer_links": []
}
```

**Field descriptions:**

- `primary_navigation` - Main site navigation (typically used in header)
- `secondary_navigation` - Alternative navigation options
- `footer_navigation` - Multiple columns of footer links with optional headers
- `footer_links` - Single list of links at the base of the page

**How it works:**

1. Each site has its own `NavigationSettings` configured in Wagtail admin
2. Frontend queries the endpoint with the appropriate `?site=` parameter
3. Settings are retrieved per-site using Wagtail's `BaseSiteSetting.for_site()` method
4. If no settings exist for a site, empty arrays are returned

**Setting up navigation in Wagtail Admin:**

1. Navigate to **Settings > Navigation Settings** in the Wagtail admin
2. Select the site you want to configure from the dropdown
3. Configure the navigation structure using StreamFields
4. Save your changes
5. The navigation will be immediately available via the API for that site

**Important notes:**

- Navigation settings are **per-site** - each site must be configured independently
- If a site has no navigation settings configured, the API returns empty arrays (not an error)
- The navigation endpoint uses the same site detection logic as other endpoints
- StreamField data is returned in its prepared JSON format via `get_prep_value()`

**TODO:**

- [ ] Review caching strategy for navigation endpoint (HTTP vs Django cache vs none) based on CDN availability and performance requirements

### Frontend Integration

For headless mode, your frontend should:

1. **Determine which site to query** based on the current domain/route
2. **Pass the site parameter** on all API requests

Example (JavaScript):

```javascript
// Configuration
const SITE_CONFIG = {
  "main.example.com": "www.nationalarchives.gov.uk",
  "site2.example.com": "localhost:8001",
};

// Get site parameter for current domain
const siteParam = SITE_CONFIG[window.location.hostname];

// Make API requests with site parameter
fetch(`/api/v2/pages/?site=${siteParam}`)
  .then((response) => response.json())
  .then((data) => console.log(data));
```

## Managing Sites in Wagtail Admin

### Creating Content for Each Site

1. Navigate to **Pages** in the Wagtail admin
2. You'll see two root pages:
   - "Home" (Site 1)
   - "Home - Site 2" (Site 2)
3. Add child pages under the appropriate root page
4. Content will automatically be filtered by site in the API

### Setting Up Site-Specific Alerts

1. Create Alert snippets in **Snippets > Alerts**
2. Navigate to the HomePage for the specific site
3. Select the alert and enable "cascade" to show it site-wide
4. The alert will only appear on that site's pages

### Viewing Site Settings

Navigate to **Settings > Sites** to:

- View all configured sites
- See hostname/port configurations
- Identify which site is the default
- **Note**: Do not delete or modify sites unless you know what you're doing

## Development

### Adding a New Site

1. Create a data migration in the appropriate app:

```python
# app/migrations/XXXX_create_third_site.py
def create_third_site(apps, schema_editor):
    ContentType = apps.get_model("contenttypes.ContentType")
    Page = apps.get_model("wagtailcore.Page")
    Site = apps.get_model("wagtailcore.Site")
    HomePage = apps.get_model("home.HomePage")

    homepage_content_type = ContentType.objects.get(
        model="homepage", app_label="home"
    )

    # Create homepage and site
    # ... (follow pattern from 0035_create_second_site.py)
```

2. Update environment variables for production:
   - Add hostname to `ALLOWED_HOSTS`
   - Configure DNS to point to your server

### Environment-Specific Hostnames

**Development:**

- Site 1: `localhost:8000` (default)
- Site 2: `localhost:8001`

**Staging/Production:**
Update site hostnames in admin or via migration:

```python
Site.objects.filter(site_name="Second Site").update(
    hostname="site2.nationalarchives.gov.uk"
)
```

## Technical Implementation

### Site Detection Flow

1. **Frontend makes API request** with optional `?site=` parameter
2. **API uses `get_site_from_request()`** utility function:
   - If `?site=` parameter present: Use specified site
   - If no parameter: Use default site (is_default_site=True)
3. **SiteFilter** filters queryset to descendants of site's root page
4. **Content returned** is scoped to that site

### Code References

- **Site detection utility**: `app/api/utils.py:5` - `get_site_from_request()`
- **Page filtering**: `app/api/filters.py` - `SiteFilter`
- **Notifications endpoint**: `app/api/urls/globals.py:17` - `GlobalsAPIViewSet.notifications_view()`
- **Navigation endpoint**: `app/api/urls/globals.py:60` - `GlobalsAPIViewSet.navigation_view()`
- **Navigation settings model**: `app/navigation/models.py:13` - `NavigationSettings`
- **Site creation migration**: `app/home/migrations/0035_create_second_site.py`

## Known Limitations

### Page Chooser in Wagtail Admin

The page chooser used in StreamFields (e.g., `PageListBlock`) currently shows pages from all sites when editors are selecting pages. This means:

- **Admin UX**: Editors will see pages from all sites in the page chooser interface
- **Actual Display**: Only explicitly selected pages are displayed on the front-end
- **Risk Level**: Low - pages from other sites only appear if explicitly chosen by an editor

**Mitigation**: This limitation is expected to be addressed by implementing site-specific user permissions in the future, which will restrict which pages editors can see and select based on their site access.

### Blog-Related Features

Blog functionality (BlogIndexPage, BlogFeedsPage, BlogPage) is currently designed for single-site use and is only used by the default site. Multi-site support for blogs has been deferred.

## Troubleshooting

### Pages from other sites appearing in API response

Make sure your frontend is passing the `?site=` parameter with the correct hostname:port combination.

### "Site not found" error

Check that:

1. The site exists in **Settings > Sites**
2. The hostname:port matches exactly (including port if using port-based sites)
3. For production, ensure DNS is configured correctly

### Global alerts not showing for second site

1. Verify the HomePage for site 2 has an alert configured
2. Check that the alert has `cascade=True` enabled
3. Confirm the alert is `active=True`

## Best Practices

1. **Always pass site parameter in headless mode** - Don't rely on defaults
2. **Use data migrations for site setup** - Keeps configuration in version control
3. **Test multi-site behavior** - Always test API endpoints with `?site=` parameter
4. **Use consistent naming** - Follow the pattern: "Home - [Site Name]"
5. **Document site purposes** - Keep track of which site is for which department

## Future Enhancements

Consider these improvements as your multi-site needs grow:

- [ ] Site-specific settings using `wagtail.contrib.settings`
- [ ] Per-site media collections
- [ ] Site-specific user permissions
- [ ] Separate frontend deployments per site
- [ ] Site-aware search functionality
