from wagtail.contrib.modeladmin.options import (
        ModelAdmin, ModelAdminGroup, modeladmin_register)
from .models import (
    HighlightsGalleryPage, Highlights, CloserLookPage)


class HighlightsGalleryAdmin(ModelAdmin):
    model = HighlightsGalleryPage
    menu_label = 'Highlights Gallery'
    menu_icon = 'folder-open-1'
    search_fields = ('title',)


class HighlightsAdmin(ModelAdmin):
    model = Highlights
    menu_label = 'Highlights'
    menu_icon = 'pick'
    search_fields = ('title',)


class CloserLookAdmin(ModelAdmin):
    model = CloserLookPage
    menu_label = 'Closer Look'
    menu_icon = 'search'
    menu_order = 200
    search_fields = ('title',)

# TODO: I've left this here as I'd like to use it for future use when we make the Highlights Gallery and Highlights, 
# but it will not be deployed with the Record Revealed deployment
# class RecordHighlightsGroup(ModelAdminGroup):
#     menu_label = 'Record Highlights'
#     menu_icon = 'folder-open-inverse'
#     menu_order = 200
#     items = (HighlightsGalleryAdmin, HighlightsAdmin, CloserLookAdmin)

# modeladmin_register(RecordHighlightsGroup)

modeladmin_register(CloserLookAdmin)