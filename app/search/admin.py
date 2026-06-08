from django.contrib import admin

from .models import ExternalApplication, ExternalApplicationPage


class ExternalApplicationPageInline(admin.TabularInline):
    model = ExternalApplicationPage
    extra = 0
    fields = ("title", "url_path", "description", "teaser_image")
    readonly_fields = ("title", "url_path", "description", "teaser_image")
    show_change_link = True
    can_delete = False


@admin.register(ExternalApplication)
class ExternalApplicationAdmin(admin.ModelAdmin):
    list_display = ("title", "version", "base_url", "type_label", "is_active", "last_updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "description", "base_url")
    readonly_fields = ("last_updated_at", "last_published_at")
    inlines = [ExternalApplicationPageInline]


@admin.register(ExternalApplicationPage)
class ExternalApplicationPageAdmin(admin.ModelAdmin):
    list_display = ("title", "application", "url_path")
    list_filter = ("application",)
    search_fields = ("title", "description", "url_path")
    readonly_fields = ("full_url",)

