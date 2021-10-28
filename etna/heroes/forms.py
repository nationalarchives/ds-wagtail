from django.utils.safestring import mark_safe

from wagtail.admin.forms import WagtailAdminPageForm


class PageWithHeroMixinForm(WagtailAdminPageForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hero_image_decorative'].label = mark_safe(
            "Is this image decorative? <p class='field-title__subheading'>Tick the box if 'yes'</p>"
        )

    def clean(self):
        cleaned_data = super().clean()

        hero_image = cleaned_data.get("hero_image")
        hero_image_decorative = cleaned_data.get("hero_image_decorative")
        hero_image_alt_text = cleaned_data.get("hero_image_alt_text")
        hero_image_caption = cleaned_data.get("hero_image_caption")

        if hero_image:
            if not hero_image_decorative and not hero_image_alt_text:
                message = "Non-decorative images must contain alt text."
                self.add_error('hero_image_alt_text', message)

            if hero_image_decorative and hero_image_alt_text:
                message = "Decorative images should not contain alt text."
                self.add_error('hero_image_decorative', message)

            if hero_image_decorative and hero_image_caption:
                message = "Decorative images should not contain a caption to prevent confusing users of assistive technologies."
                self.add_error('hero_image_caption', message)

        return cleaned_data
