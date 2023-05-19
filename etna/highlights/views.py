from django.db.models import Q

from wagtail.admin.views.generic.chooser import CreateView
from wagtail.images import get_image_model
from wagtail.models import Collection
from wagtail.search import index as search_index
from wagtail.snippets.views.chooser import SnippetChooserViewSet

from .forms import HighlightCreateStep1Form, HighlightCreateStep2Form


class HighlightChooserCreateView(CreateView):
    @property
    def target_image_collection(self):
        # Return the collection that uploaded image files should be
        # added to when creating CustomImage objects
        return (
            Collection.objects.filter(Q(name="Highlights") | Q(depth=1))
            .order_by("-depth")
            .first()
        )

    def post(self, request):
        current_step = 2 if request.POST["step"] == "2" else 1

        self.form = self.get_creation_form(current_step)

        if not self.form.is_valid():
            return self.get_reshow_creation_form_response()

        if current_step == 1:
            # Find record details to set default values
            record = None
            if len(self.form.cleaned_data["record_matches"]) == 1:
                record = self.form.cleaned_data["record_matches"][0]
            else:
                for r in self.form.cleaned_data["record_matches"]:
                    if r.reference_number == self.form.cleaned_data["record_reference"]:
                        record = r
                        break

            # Define initial data for step 2 form
            initial = {}
            if record:
                initial = {
                    "record": record.iaid,
                    "title": record.summary_title[:255],
                    "description": record.listing_description,
                }

            # If provided, create an image from the uploaded file
            if image_file := self.form.cleaned_data.get("teaser_image"):
                if record:
                    image_title = f"{record.summary_title[:225]} ({record.reference_number or record.iaid})"
                else:
                    image_title = "Highlight image"

                image = get_image_model()(
                    file=image_file,
                    title=image_title,
                    collection=self.target_image_collection,
                )
                image._set_image_file_metadata()
                image.save()
                initial["teaser_image"] = image.pk
                search_index.insert_or_update_object(image)

            # Show a pre-populated 'step two' form to complete the process
            self.form = self.get_creation_form(
                2,
                record_choices=[
                    (match.iaid, str(match))
                    for match in self.form.cleaned_data["record_matches"]
                ],
                initial=initial,
                data=None,
                files=None,
            )
            return self.get_reshow_creation_form_response()
        else:
            object = self.save_form(self.form)
            if object.teaser_image:
                # copy edited highlight title to the uploaded image
                object.teaser_image.title = object.title
                object.teaser_image.save()
            return self.get_chosen_response(object)

    def get_creation_form(self, step: int, **init_kwargs):
        if step == 1:
            form_class = HighlightCreateStep1Form
        else:
            form_class = HighlightCreateStep2Form
        kwargs = self.get_creation_form_kwargs()
        kwargs.update(init_kwargs)
        return form_class(**kwargs)


class HighlightChooserViewSet(SnippetChooserViewSet):
    create_view_class = HighlightChooserCreateView
    creation_form_class = HighlightCreateStep1Form
