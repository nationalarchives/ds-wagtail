from wagtail.users.views.users import IndexView
from wagtail.users.views.users import UserViewSet as WagtailUserViewSet


# ==========================================
# For now this is a VERY QUICK AND DIRTY way
# to filter out users without passwords i.e.
# users set up without a password so that we
# can set them up with a token to access the
# API - this will mean they won't show up in
# the Wagtail admin interface user list, and
# so can't be changed accidentally, although
# they CAN still be edited by visiting their
# user edit page directly
# ==========================================
class CustomIndexView(IndexView):
    def order_queryset(self, queryset):
        queryset = super().order_queryset(queryset)
        users_with_password = [
            user.id for user in queryset if user.has_usable_password()
        ]
        return queryset.filter(id__in=users_with_password)


class UserViewSet(WagtailUserViewSet):
    index_view_class = CustomIndexView
