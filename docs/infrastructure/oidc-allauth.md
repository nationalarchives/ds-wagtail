# OpenID Connect (OIDC) with django-allauth — Implementation Notes

ds-wagtail integrates Entra (Azure AD) via OpenID Connect using `django-allauth`'s OpenID Connect provider. It has a small adapter (IT controls access; Wagtail controls permissions).

- Protocol: OpenID Connect (OIDC)
- Library: `django-allauth` with the `idp-oidc` extra
- Provider id: `entra`
- Goal: IT manages a single Entra group (or Enterprise Application assignment) to grant
  access. Wagtail admins manage permissions inside the CMS.
