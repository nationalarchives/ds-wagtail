from wagtail.contrib.modeladmin.options import (
        ModelAdmin, ModelAdminGroup, modeladmin_register)
from .models import (
    HighlightsGalleryPage, Highlights, CloserLookPage)


class HighlightsGalleryAdmin(ModelAdmin):
    model = HighlightsGalleryPage
    menu_label = 'Highlights Gallery'
    menu_icon = 'folder-open-1'
    #list_display = ('title')
    #list_filter = ('tags')
    search_fields = ('title',)


class HighlightsAdmin(ModelAdmin):
    model = Highlights
    menu_label = 'Highlights'
    menu_icon = 'pick'
    #list_display = ('title',)
    #list_filter = ('tags',) can use this for tags?
    search_fields = ('title',)


class CloserLookAdmin(ModelAdmin):
    model = CloserLookPage
    menu_label = 'Closer Look'
    menu_icon = 'search'
    menu_order = 200 # Remove when uncommenting the below code
    #list_display = ('title',)
    #list_filter = ('title',)
    search_fields = ('title',)

# Leaving this here until HighlightsGallery and Highlights are going live.
# class RecordHighlightsGroup(ModelAdminGroup):
#     menu_label = 'Record Highlights'
#     menu_icon = 'folder-open-inverse'
#     menu_order = 200
#     items = (HighlightsGalleryAdmin, HighlightsAdmin, CloserLookAdmin)

# modeladmin_register(RecordHighlightsGroup)

modeladmin_register(CloserLookAdmin)