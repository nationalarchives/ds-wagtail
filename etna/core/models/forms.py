from wagtail.admin.forms import WagtailAdminPageForm

__all__ = ["RequiredHeroImagePageForm"]


class RequiredHeroImagePageForm(WagtailAdminPageForm):
    """
    Overriding the base form class on select pages to allow for 'required' decorative
    images that do not impact the function of the page. This allows for a non-required field
    in the database, but a required field in the front-end, so that the hero_image cannot be
    blank. This satisfies test cases as the hero_image doesn't need to be set.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["hero_image"].required = True
