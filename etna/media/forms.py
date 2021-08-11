import magic

from django import forms
from django.core.exceptions import ValidationError

from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.admin import widgets

from wagtailmedia.permissions import permission_policy as media_permission_policy
from wagtail.admin.forms.collections import BaseCollectionMemberForm, collection_member_permission_formset_factory


class BaseMediaForm(BaseCollectionMemberForm):
    class Meta:
        widgets = {
            "date": widgets.AdminDateInput,
            "tags": widgets.AdminTagWidget,
            "file": forms.FileInput,
            "thumbnail": forms.ClearableFileInput,
        }

    permission_policy = media_permission_policy

    def __init__(self, *args, **kwargs):
        super(BaseMediaForm, self).__init__(*args, **kwargs)

        # Remove unused width & height fields.
        for name in ("width", "height"):
            # these fields might be editable=False so verify before accessing
            if name in self.fields:
                del self.fields[name]

    def clean_file(self):
        error_messages = {
            "mime_type": "%(filename)s is not a valid %(type)s file.",
        }

        data = self.cleaned_data['file']
        mime_type = magic.from_buffer(data.read(), mime=True)
        data.seek(0)

        params = {
            "filename": data,
            "type": self.instance.type,
        }

        # Ensure file is a valid type for the current instance.
        if self.instance.type == "audio":
            if mime_type != "audio/mpeg":
                raise ValidationError(error_messages["mime_type"], params=params)
        else:
            if mime_type != "video/mp4":
                raise ValidationError(error_messages["mime_type"], params=params)

        return data
