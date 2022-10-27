from wagtail.contrib.modeladmin.options import (ModelAdmin, modeladmin_register)
from .models import Highlights


class HighlightsAdmin(ModelAdmin):
    model = Highlights
    base_url_path = 'highlights'
    menu_label = 'Highlights'
    menu_icon = 'pick'
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    add_to_admin_menu = True
    list_display = ('title', 'image')
    #list_filter = ('',) can use this for tags?
    search_fields = ('title')


modeladmin_register(HighlightsAdmin)


""" FOR LATER USE WHEN THERE ARE MORE MODELS/PAGES
from wagtail.contrib.modeladmin.options import (
        ModelAdmin, ModelAdminGroup, modeladmin_register)
    from .models import (
        HighlightsGalleryPage, Highlights, CloserLookPage)


    class HighlightsGalleryAdmin(ModelAdmin):
        model = HighlightsGalleryPage
        menu_label = 'Highlights Gallery'
        menu_icon = 'folder-open-1'  # change as required
        list_display = ('title', 'author')
        list_filter = ('genre', 'author')
        search_fields = ('title', 'author')


    class HighlightsAdmin(ModelAdmin):
        model = Highlights
        base_url_path = 'highlights'
        menu_label = 'Highlights'
        menu_icon = 'pick'
        list_display = ('title', 'image')
        #list_filter = ('',) can use this for tags?
        search_fields = ('title')


    class CloserLookAdmin(ModelAdmin):
        model = CloserLookPage
        menu_label = 'Closer Look'
        menu_icon = 'search'
        list_display = ('name',)
        list_filter = ('name',)
        search_fields = ('name',)


    class RecordHighlightsGroup(ModelAdminGroup):
        menu_label = 'Record Highlights'
        menu_icon = 'folder-open-inverse'
        menu_order = 200
        items = (HighlightsGalleryAdmin, HighlightsAdmin, CloserLookAdmin)

    modeladmin_register(RecordHighlightsGroup)"""