from django.urls import reverse
from django.utils.http import urlencode

from etna.ciim.constants import BucketKeys, TimelineTypes, VisViews

# visualisation urls
VIS_URLS = {
    VisViews.LIST.value: f'{reverse("search-catalogue")}?{urlencode({"group": BucketKeys.COMMUNITY, "vis_view": VisViews.LIST})}',
    VisViews.MAP.value: f'{reverse("search-catalogue")}?{urlencode({"group": BucketKeys.COMMUNITY, "vis_view": VisViews.MAP})}',
    VisViews.TIMELINE.value: f'{reverse("search-catalogue")}?{urlencode({"group": BucketKeys.COMMUNITY, "vis_view": VisViews.TIMELINE, "timeline_type": TimelineTypes.CENTURY})}',
    VisViews.TAG.value: f'{reverse("search-catalogue")}?{urlencode({"group": BucketKeys.COMMUNITY, "vis_view": VisViews.TAG})}',
}
