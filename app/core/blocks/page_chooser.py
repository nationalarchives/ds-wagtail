from wagtail import blocks

from app.core.serializers.pages import get_api_data


class APIPageChooserBlock(blocks.PageChooserBlock):
    def __init__(
        self,
        page_type=None,
        can_choose_root=False,
        target_model=None,
        required_api_fields=[],
        **kwargs,
    ):
        self.required_api_fields = required_api_fields
        super().__init__(
            page_type=page_type,
            can_choose_root=can_choose_root,
            target_model=target_model,
            **kwargs,
        )

    def get_api_representation(self, value, context=None):
        return get_api_data(object=value, required_api_fields=self.required_api_fields)
