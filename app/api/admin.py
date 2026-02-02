from django.contrib import admin

from .models import APIToken


class APITokenAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "active", "created")
    list_filter = ("active", "created")
    search_fields = ("name", "key")
    readonly_fields = ("key", "created")
    ordering = ("-created",)

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
