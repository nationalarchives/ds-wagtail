import magic

from django import forms
from django.core.exceptions import ValidationError

from wagtail.admin import widgets

from wagtailmedia.permissions import permission_policy as media_permission_policy
from wagtail.admin.forms.collections import BaseCollectionMemberForm

from django.forms.models import modelform_factory


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

        # Remove unused fields.
        for name in ("width", "height", "thumbnail"):
            # these fields might be editable=False so verify before accessing
            if name in self.fields:
                del self.fields[name]

    def clean_file(self):
        error_messages = {
            "mime_type": "%(filename)s (%(mime_type)s) is not an allowed %(type)s file.",
        }

        audio_types = [
            "audio/mpeg",
        ]

        video_types = [
            "video/mp4",
        ]

        data = self.cleaned_data['file']
        mime_type = magic.from_buffer(data.read(), mime=True)
        data.seek(0)

        params = {
            "filename": data,
            "mime_type": mime_type,
            "type": self.instance.type,
        }

        # Ensure file is a valid type for the current instance.
        if self.instance.type == "audio":
            if mime_type not in audio_types:
                raise ValidationError(error_messages["mime_type"], params=params)
        else:
            if mime_type not in video_types:
                raise ValidationError(error_messages["mime_type"], params=params)

        return data
