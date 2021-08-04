from django.conf.urls import url
from django.http import FileResponse
from django.shortcuts import render, Http404

from generic_chooser.views import ModelChooserViewSet, ModelChooserMixin, BaseChosenView

from .models import Image, RecordPage
from ..ciim.exceptions import DoesNotExist, KongException


def record_page_disambiguation_view(request, reference_number):
    """View to render a record's details page or disambiguation page if multiple records are found.

    Details pages differ from all other page types within Etna in that their
    data isn't fetched from the CMS but an external API. And unlike standrard
    Wagtail pages, this view is accessible from a fixed URL.

    Fetches by reference_number may return multiple results.

    For example ADM 223/3. This is both the catalogue reference for 1 piece and
    for the 499 item records within:

    https://discovery.nationalarchives.gov.uk/browse/r/h/C4122893
    """
    pages = RecordPage.search.filter(ref=reference_number, pretty=True)

    if len(pages) == 0:
        raise Http404

    # if the results contain a single record page, render the details page.
    if len(pages) == 1:
        page = pages[0]

        return render(
            request,
            page.get_template(request),
            {
                "page": page,
            },
        )

    return render(
        request,
        "records/record_disambiguation_page.html",
        {
            "pages": pages,
            "queried_reference_number": reference_number,
        },
    )


def record_page_view(request, iaid):
    """View for rendering a record's details page.

    Details pages differ from all other page types within Etna in that their
    data isn't fetched from the CMS but an external API. And unlike pages, this
    view is accessible from a fixed URL.
    """
    try:
        page = RecordPage.search.get(iaid)
    except DoesNotExist:
        raise Http404

    image = Image.search.filter(rid=page.media_reference_id).first()

    return render(
        request,
        page.get_template(request),
        {
            "page": page,
            "image": image,
        },
    )


def image_serve(request, location):
    """Relay content served from Kong's /media endpoint"""
    response = Image.media.serve(location)

    if not response.ok:
        raise Http404

    return FileResponse(
        response.raw,
        content_type="image/jpeg",
        reason=response.reason,
    )


class KongModelChooserMixinIn(ModelChooserMixin):
    """Chooser source to allow filtering and selection of Kong model data.

    Similar to the DFRDRFChooserMixin:

    https://github.com/wagtail/wagtail-generic-chooser/blob/9ec9db937fe40311c67ed055e1b3f0dcd1b86908/generic_chooser/views.py#L223
    """

    def get_object_list(self, search_term=""):
        """Filter object list by user's search term"""
        object_list = self.get_unfiltered_object_list()

        if search_term:
            object_list = self.model.search.filter(
                term=search_term, stream="evidential"
            )

        return object_list

    def get_object(self, pk):
        """Fetch selected object"""
        return self.model.search.get(iaid=pk)

    def get_object_id(self, instance):
        """Return selected object's ID, used when resolving a link to this item.

        see RecordChooserViewSet.get_urlpatterns for overridden pattern for selected item.
        """
        return instance.iaid

    def user_can_create(self, user):
        """Records cannot be created in Wagtail.

        Hides the "create" tab in chooser.
        """
        return False


class KongChosenView(BaseChosenView):
    """View to handle fetching a selected item."""

    def get(self, request, pk):
        """Fetch selected item by its pk (in our case IAID)

        Override parent to handle any errors from the Kong API.
        """
        try:
            return super().get(request, pk)
        except KongException:
            raise Http404


class RecordChooserViewSet(ModelChooserViewSet):
    """Custom chooser to allow users to filter and select records."""
    base_chosen_view_class = KongChosenView
    chooser_mixin_class = KongModelChooserMixinIn
    icon = "form"
    model = RecordPage
    page_title = "Choose a record"
    per_page = 10
    order_by = "iaid"
    fields = ["iaid", "title"]

    def get_urlpatterns(self):
        """Define patterns for chooser and chosen views.

        Overridden to allow IAID to be used as an ID for chosen view"""
        return super().get_urlpatterns() + [
            url(r"^$", self.choose_view, name="choose"),
            url(r"^([\w-]+)/$", self.chosen_view, name="chosen"),
        ]
