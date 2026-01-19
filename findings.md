# Findings & Architectural Notes

This document captures architectural patterns, design decisions, and implementation findings discovered while working on the codebase. It serves as a reference for understanding trade-offs and potential refactoring opportunities.

---

## Call to Action (CTA) Implementation

**Current Implementation:** StreamField Blocks
**Alternative Approach:** Snippets
**Status:** ⚠️ Creates overhead for reusable content

### Current Approach

CTAs are implemented as inline StreamField blocks (`CallToActionBlock`) that are added directly into page content streams.

**Code references:**

- Block definition: `app/core/blocks/cta.py:73`
- Usage example: `app/ukgwa/blocks.py:41`

**Structure:**

```python
class CallToActionBlock(blocks.StructBlock):
    body = APIRichTextBlock(max_length=100)
    button = ButtonBlock()  # Contains label, link/external_link, accented flag
```

**How it's used:**

```python
class StoryBlock(blocks.StreamBlock):
    # ... other blocks ...
    call_to_action = CallToActionBlock()
```

### Problem: Reusability Overhead

When using StreamField blocks for CTAs:

1. **Content duplication** - Each CTA is defined inline within the page content. If the same CTA appears on multiple pages, the content must be duplicated across all pages.

2. **Update overhead** - Changing a reusable CTA (e.g., "Sign up for our newsletter" or "Book a visit") requires:
   - Finding all pages that use it
   - Manually updating each instance
   - Risk of inconsistency if updates are missed

3. **No centralized management** - Editors cannot see all CTAs in one place or track which pages use which CTAs.

4. **API payload bloat** - Each page's API response includes the full CTA data, even when CTAs are identical across pages.

### Alternative: Snippet-Based CTAs

A commented-out implementation exists showing the snippet approach:

**Code reference:** `app/ukgwa/blocks.py:42-47`

```python
# Alternative (commented out):
call_to_action = SnippetChooserBlock(
    "core.CallToActionSnippet",
    label="Call To Action",
    template="components/streamfield/call_to_action_block.html",
)
```

**How snippet-based CTAs work:**

1. Create reusable CTA snippets in Wagtail admin (Settings > CTAs)
2. Editors choose from existing CTAs when building page content
3. Changes to a CTA snippet propagate to all pages that reference it
4. API can return CTA by reference (ID) or inline (depending on serializer configuration)

### Trade-offs

| Aspect                  | StreamField Blocks (Current)   | Snippets                                |
| ----------------------- | ------------------------------ | --------------------------------------- |
| **Content reuse**       | ❌ Must duplicate content      | ✅ Reference single snippet             |
| **Updates**             | ❌ Update each instance        | ✅ Update once, affects all             |
| **Editor experience**   | ✅ Simple inline editing       | ⚠️ Extra step to create/choose          |
| **Flexibility**         | ✅ Unique CTA per page         | ⚠️ Must create snippet for one-off CTAs |
| **API efficiency**      | ⚠️ Full data in every response | ✅ Can use references or shared data    |
| **Management overhead** | ✅ No extra model needed       | ⚠️ Requires snippet model + admin       |
| **Use case fit**        | ✅ Great for unique CTAs       | ✅ Great for reusable CTAs              |

### Recommendations

**Use StreamField blocks when:**

- CTAs are unique to each page
- Content is unlikely to be reused
- Editors need inline editing workflow
- Simplicity is prioritized over reusability

**Use Snippets when:**

- CTAs are reused across multiple pages (e.g., newsletter signup, booking links)
- Consistent messaging is critical
- Centralized management is valuable
- Updates need to propagate globally

### Potential Hybrid Approach

Support both patterns in the same StreamField:

```python
class StoryBlock(blocks.StreamBlock):
    # Inline CTA for unique content
    call_to_action = CallToActionBlock()

    # Reusable CTA from snippet library
    reusable_call_to_action = SnippetChooserBlock(
        "core.CallToActionSnippet",
        label="Reusable Call To Action",
    )
```

This gives editors flexibility to choose the right approach per use case.

### Related Patterns

This finding applies to other potentially reusable content types:

- Testimonials / quotes
- Contact information blocks
- Alert/notification banners
- Partner logos (currently uses snippets - see `app/core/models/partner_logos.py`)
- Featured links/cards

---

## API Caching Strategy for Headless CMS

**Current Implementation:** No caching (commented out)
**Status:** ⚠️ Needs review based on infrastructure

### Context

For the navigation endpoint (`/api/v2/globals/navigation/`), caching logic exists but is currently commented out.

**Code reference:** `app/api/urls/globals.py:76-82, 104`

### The Headless CMS Consideration

In a headless CMS architecture, the frontend typically:

- Fetches navigation data once on application load
- Stores it in application state (React Context, Redux, Vuex, etc.)
- Doesn't re-fetch until page refresh or app restart

This changes the caching strategy significantly compared to traditional server-rendered applications.

### Caching Options

| Strategy         | When It Helps                          | Trade-offs                                                      |
| ---------------- | -------------------------------------- | --------------------------------------------------------------- |
| **Django Cache** | Reduces DB queries across all requests | Requires Redis/Memcached; needs cache invalidation on updates   |
| **HTTP Caching** | Browser/CDN can cache responses        | Only helps if CDN is in front of API; 1st request still hits DB |
| **No Caching**   | Query is cheap (1 lookup + JSON field) | Simplest; minimal performance impact for lightweight queries    |

### Current Query Cost

```python
navigation_settings = NavigationSettings.for_site(site)  # 1 DB query
data = {
    "field": navigation_settings.field.get_prep_value(),  # No query, JSON field
}
```

- **Single database query** per request
- **StreamField data** already stored as JSON (fast retrieval)
- **Performance impact**: ~10ms per request

### Recommendation

**Start without server-side caching** because:

1. ✅ Single DB query is inexpensive
2. ✅ Frontend manages caching in application state
3. ✅ Simpler implementation and maintenance
4. ✅ No cache invalidation complexity

**Add caching only if:**

- You have a CDN (Cloudflare, Fastly) → Use HTTP caching headers
- You see performance issues → Add Django cache with signal-based invalidation
- You have Redis/Memcached for other purposes → Can piggyback on existing infrastructure

### If Implementing Django Cache

Use a hybrid approach with signal-based invalidation:

```python
# In model
@receiver(post_save, sender=NavigationSettings)
def clear_navigation_cache(sender, instance, **kwargs):
    cache.delete(f"site_navigation_{instance.site_id}")

# In view
# Long Django cache (cleared on save) + short HTTP cache
response['Cache-Control'] = 'public, max-age=60'  # 1 minute
cache.set(cache_key, data, 900)  # 15 minutes
```

**Max staleness:** 1 minute (acceptable for most CMS use cases)

**Related documentation:** See multi-site-setup.md "Navigation Settings" section

---

## Multi-Site: Page Chooser Cross-Site Visibility

**Current Behavior:** Page chooser shows pages from all sites
**Status:** ⚠️ Known limitation - Low risk

### The Issue

When editors use the page chooser in StreamFields (e.g., `PageListBlock`, `APIPageChooserBlock`), they see pages from **all sites** in the selection interface, not just pages from their current site.

**Code references:**

- Page chooser block: `app/core/blocks/page_chooser.py`
- Used in: Various StreamField blocks throughout the codebase

### Impact

- **Admin UX**: Editors working on Site A will see pages from Site B in the chooser
- **Actual Display**: Only explicitly selected pages appear on frontend (no data leakage)
- **Risk Level**: Low - pages from other sites only appear if explicitly chosen by an editor

### Why This Happens

Wagtail's page chooser doesn't automatically filter by site context. It shows all live pages that the user has permission to see.

### Current Mitigation

**Editor training**: Editors need to be aware they're working on a specific site and should only select pages from that site's page tree.

### Future Solution

**Site-specific user permissions**: Implementing Wagtail's user permissions to restrict which page trees editors can access. This would:

1. Limit page chooser to show only relevant site's pages
2. Prevent editors from accidentally selecting wrong-site pages
3. Improve admin UX for multi-site setups

**Status:** Deferred - will be addressed when implementing site-specific user permissions

**Related documentation:** See multi-site-setup.md "Known Limitations" section

---

## Blog Features: Single-Site Only

**Current Implementation:** Blog designed for single-site use
**Status:** ⚠️ Intentional limitation

### Affected Features

Blog functionality is currently only used by the default site:

- `BlogIndexPage` - Main blog listing
- `BlogFeedsPage` - RSS/Atom feeds
- `BlogPage` - Individual blog posts

**Code reference:** `app/blog/models.py`

### Why Single-Site

Blogs require additional considerations for multi-site:

1. **URL structure** - Each site would need its own `/blog/` path
2. **Feeds** - RSS feeds would need to be site-specific
3. **Categorization** - Tags/categories might overlap or conflict between sites
4. **Author attribution** - Authors might write for multiple sites

### Decision

Multi-site blog support has been **intentionally deferred** because:

- Only the default site currently uses blog features
- Adds significant complexity for uncertain future value
- Can be added later if needed

### If Multi-Site Blogs Are Needed

Consider these approaches:

**Option 1: Separate blog apps per site**

- Each site gets its own blog page tree
- Simplest to implement
- Duplicate blog infrastructure

**Option 2: Shared blog content with site filtering**

- Single blog system with `site` foreign key on `BlogPage`
- More complex filtering logic
- Allows cross-site blog post sharing

**Related documentation:** See multi-site-setup.md "Known Limitations" section

---

## Future Findings

Additional architectural notes and findings will be documented here as they are discovered.
