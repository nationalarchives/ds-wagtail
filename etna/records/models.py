from wagtail.core.models import Page


class RecordPage(Page):
    """Non-creatable page used to render record data in templates. 

    This stub page allows us to use common templates to render external record
    data as though the data was fetched from the CMS.

    see: views.record_page_view
    """
    is_creatable = False
