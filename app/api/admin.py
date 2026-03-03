from django.contrib import admin

from .models import APIToken


class APITokenAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "active", "created", "updated")
    list_filter = ("active", "created", "updated")
    search_fields = ("name",)
    readonly_fields = ("key", "created", "updated")
    ordering = ("-updated",)

    fieldsets = (
        (None, {"fields": ("name", "active")}),
        (
            "Token Information",
            {
                "fields": ("key", "created"),
                "description": "The token key is automatically generated and cannot be changed.",
            },
        ),
    )


admin.site.register(APIToken, APITokenAdmin)
