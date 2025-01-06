import magic
from django import forms
from django.core.exceptions import ValidationError
from wagtail.admin import widgets
from wagtail.admin.forms.collections import BaseCollectionMemberForm
from wagtailmedia.permissions import permission_policy as media_permission_policy

# Valid audio/video media types - https://www.iana.org/assignments/media-types/media-types.xhtml
ALLOWED_AUDIO_MIME_TYPES = [
    "audio/mpeg",
]
ALLOWED_VIDEO_MIME_TYPES = [
    "video/mp4",
]


class BaseMediaForm(BaseCollectionMemberForm):
    class Meta:
        widgets = {
            "date": widgets.AdminDateInput,
            "tags": widgets.AdminTagWidget,
            "file": forms.FileInput,
        }

    permission_policy = media_permission_policy

    def __init__(self, *args, **kwargs):
        super(BaseMediaForm, self).__init__(*args, **kwargs)

        # Remove unused fields - as is done for audio only in wagtailmedia BaseMediaForm.__init__
        # https://github.com/torchbox/wagtailmedia/blob/28f0df495661d8fc9f4e573daf3b446a55bbbfab/wagtailmedia/forms.py#L38
        for name in ("width", "height", "thumbnail"):
            if name in self.fields:
                del self.fields[name]

    def clean_file(self):
        error_messages = {
            "mime_type": "%(filename)s (%(mime_type)s) is not an allowed %(type)s file.",
        }

        data = self.cleaned_data["file"]
        mime_type = magic.from_buffer(data.read(), mime=True)
        data.seek(0)

        params = {
            "filename": data,
            "mime_type": mime_type,
            "type": self.instance.type,
        }

        # Ensure file is a valid type for the current instance.
        if self.instance.type == "audio":
            if mime_type not in ALLOWED_AUDIO_MIME_TYPES:
                raise ValidationError(error_messages["mime_type"], params=params)
        else:
            if mime_type not in ALLOWED_VIDEO_MIME_TYPES:
                raise ValidationError(error_messages["mime_type"], params=params)

        return data
