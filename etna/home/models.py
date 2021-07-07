from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.core.models import Page, Orderable
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    PageChooserPanel,
)
from wagtail.core.fields import RichTextField


class HomePageRelatedContent(Orderable):
    page = ParentalKey('home.HomePage', related_name='related_content')
    related = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Promoted page'
    )

    panels = [PageChooserPanel('related')]


class HomePage(Page):
    introduction = models.CharField(max_length=200, blank=True)
    information = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        InlinePanel('related_content', max_num=3, label='Promoted pages'),
        FieldPanel('information'),
    ]
