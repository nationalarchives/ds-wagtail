import copy
import importlib
import logging
import re

from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

from django.conf import settings
from django.core.paginator import Page as PaginatorPage
from django.forms import Form
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from django.views.generic import FormView, TemplateView

from wagtail.coreutils import camelcase_to_underscore

from ..analytics.mixins import SearchDataLayerMixin
from ..ciim.client import Aggregation, Sort, Stream
from ..ciim.constants import (
    CATALOGUE_BUCKETS,
    CLOSURE_CLOSED_STATUS,
    Bucket,
    BucketKeys,
    BucketList,
    Display,
    SearchTabs,
    TimelineTypes,
    VisViews,
)
from ..ciim.paginator import APIPaginator
from ..ciim.utils import underscore_to_camelcase
from ..records.api import records_client
from .forms import CatalogueSearchForm

logger = logging.getLogger(__name__)


class BucketsMixin:
    """
    A mixin for views that display a list of 'buckets' to a user.

    The `bucket_list` attribute should be set to one of the `BucketList`
    values from `etna.ciim.constants`. This value is copied and enhanced
    in the `get_buckets_for_display()` method to make the value more useful
    for rendering, then added to the template context as "buckets" by
    `get_context_data()`
    """

    # The source data for get_buckets_for_display()
    bucket_list: BucketList = None

    # To be updated by the view in get() or post()
    current_bucket_key: str = None
    current_bucket: Bucket = None

    def get_bucket_counts(self) -> List[Dict[str, Union[str, int]]]:
        """
        Returns a list of dicts that are used by `get_buckets_for_display()`
        to set the `result_count` attribute for each bucket.
        """
        return self.api_result.bucket_counts

    def get_current_bucket_key(self) -> Optional[str]:
        """
        Returns the key of the 'currently active' bucket, where relevant.
        Used by `get_buckets_for_display()` to set the 'is_current' attribute
        value to `True` on the matching bucket.
        """
        return self.current_bucket_key

    def get_buckets_for_display(self) -> Optional[BucketList]:
        """
        Returns a modified `BucketList` value that can be used in the template,
        representing the 'buckets' that available for the user to explore.
        """
        if not self.bucket_list:
            return None

        bucket_list = copy.deepcopy(self.bucket_list)

        # set `result_count` for each bucket
        doc_counts_by_key = {
            group["value"]: group["doc_count"] for group in self.get_bucket_counts()
        }
        for bucket in bucket_list:
            bucket.result_count = doc_counts_by_key.get(bucket.key, 0)

        if current := self.get_current_bucket_key():
            # set 'is_current=True' for the relevant bucket
            for bucket in bucket_list:
                if bucket.key == current:
                    bucket.is_current = True
                    break

        return bucket_list

    def get_context_data(self, **kwargs):
        buckets = self.get_buckets_for_display()

        # Set this to True if any buckets have results
        buckets_contain_results = False
        for bucket in buckets:
            if bucket.result_count:
                buckets_contain_results = True
                break

        return super().get_context_data(
            buckets=buckets, buckets_contain_results=buckets_contain_results, **kwargs
        )


class ClientAPIMixin:
    """
    A mixin for views that call the Client API to retrieve and display
    records.
    """

    # The name of the method on the API client to request from
    api_method_name: str = ""

    def get_api_result(self, form: Form) -> Dict[str, Any]:
        """
        Queries the API, and returns a `dict` containing any data from the
        response that is useful for the request.
        """
        # variabalize the method for calling below
        client_method_to_call = getattr(records_client, self.api_method_name)
        # call the variabalized api client method
        response = client_method_to_call(**self.get_api_kwargs(form))
        # add response to view state for use in other methods
        self.api_result = response
        return response

    def get_api_kwargs(self, form: Form) -> Dict[str, Any]:
        """
        Return a `dict` of key/value pairs for `get_api_result()` to use
        when making the request.
        """
        raise NotImplementedError

    def process_api_result(self, form: Form, api_result: Dict[str, Any]):
        """
        A hook that allows views to take any additional actions after
        succesfully querying the API, and before rendering the response to
        a template.
        """
        # do nothing by default
        pass

    def paginate_api_result(
        self, result_list: List[Dict[str, Any]], per_page: int, total_count: int
    ) -> Tuple[APIPaginator, PaginatorPage, Iterator[int]]:
        """
        Returns pagination-related objects to facilitate rendering of
        pagination links etc. The correct page of results should have
        already been fetched from the API by this point, so the paginator
        has no impact on the results that are displayed.
        """
        paginator = APIPaginator(total_count, per_page=per_page)
        page = PaginatorPage(result_list, number=self.page_number, paginator=paginator)
        page_range = paginator.get_elided_page_range(
            number=self.page_number, on_each_side=1, on_ends=1
        )
        return paginator, page, page_range


class SearchLandingView(SearchDataLayerMixin, BucketsMixin, TemplateView):
    """
    A simple view that queries the API to retrieve counts for the various
    buckets the user can explore, and provides a form to encourage the user
    to dig deeper. Any interaction should take them to one of the other,
    more sophisticated, views below.

    Although this view called the Client API, it does not use ClientAPIMixin,
    as the unique functionality is simple enough to keep in a single method.
    """

    template_name = "search/search.html"
    bucket_list = CATALOGUE_BUCKETS
    page_type = "Search landing page"
    page_title = "Search landing"

    def get_context_data(self, **kwargs):
        # Make empty search to get aggregations
        self.api_result = records_client.search(
            aggregations=[
                Aggregation.CATALOGUE_SOURCE,
                Aggregation.CLOSURE,
                Aggregation.COLLECTION,
                Aggregation.LEVEL,
                Aggregation.TOPIC,
                # Fetching more groups so that we receive a counts
                # for any bucket/tab options we might be showing
                f"{Aggregation.GROUP}:30",
                Aggregation.HELD_BY,
                Aggregation.TYPE,
            ],
            size=0,
        )
        kwargs["page_type"] = self.page_type
        kwargs["page_title"] = self.page_title
        return super().get_context_data(
            meta_title="Search the collection",
            form=CatalogueSearchForm(),
            **kwargs,
        )


class GETFormView(FormView):
    """
    A customised version of Django's FormView that processes the form on GET
    requests (using querystring data), rather than POST requests.

    To learn more about FormView, see:
    * https://docs.djangoproject.com/en/stable/topics/class-based-views/generic-editing/
    * https://ccbv.co.uk/projects/Django/stable/django.views.generic.edit/FormView/
    """

    http_method_names = ["get", "head"]

    def setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        """
        Create a form instance that any method can use, then bind and validate it.
        """
        super().setup(request, *args, **kwargs)
        self.form = self.get_form()
        self.form.is_valid()

    def get(self, request: HttpRequest, **kwargs: Any) -> HttpResponse:
        """
        Overrides FormView.get() to process the form and continue to
        form_valid() or form_invalid() as appropriate.
        """
        if self.form.is_valid():
            return self.form_valid(self.form)
        return self.form_invalid(self.form)

    def process_valid_form(self, form: Form) -> None:
        """
        A hook that allows views to take any additional actions after
        the form has been validated, but before gathering context data
        and rendering the response.
        """
        return None

    def form_valid(self, form: Form) -> HttpResponse:
        """
        Instead of the redirecting to success_url (FormView behaviour),
        continue with rendering.
        """
        self.process_valid_form(form)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_form_kwargs(self) -> Dict[str, Any]:
        """
        Overrides FormView.get_form_kwargs() to use `request.GET` for data
        instead `request.POST`. Thes values are used by FormView.get_form()
        to initialise the form object used by the view.
        """
        kwargs = super().get_form_kwargs()

        data = self.request.GET.copy()

        # Add any initial values
        for k, v in kwargs.get("initial", {}).items():
            data.setdefault(k, v)

        kwargs["data"] = data
        return kwargs


class BaseSearchView(SearchDataLayerMixin, ClientAPIMixin, GETFormView):
    """
    A base view that extends GETFormView to call the API when the form
    data is valid, and render results to a template.
    """

    base_title = "Search results"

    http_method_names = ["get", "head"]

    def setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        super().setup(request, *args, **kwargs)
        self.query = self.form.cleaned_data.get("q", "")
        self.api_result = None
        self.current_bucket_key = self.form.cleaned_data.get("group")
        if self.current_bucket_key and getattr(self, "bucket_list", None):
            self.current_bucket = self.bucket_list.get_bucket(self.current_bucket_key)

    def process_valid_form(self, form: Form) -> HttpResponse:
        """
        When the form is valid, get results from the API, take any actions
        based on the result, then render everything to a template.
        """
        self.api_result = self.get_api_result(form)
        self.process_api_result(form, self.api_result)

    def get_meta_title(self) -> str:
        """
        Return a string to use the the <title> tag for this view.
        """
        title = self.base_title
        if self.query:
            title += ' for "' + self.query.replace('"', "'") + '"'
        return title

    def get_result_count(self) -> int:
        """
        Return the total number of results that match the user's search terms
        and/or filter preferences.

        NOTE: Views using an API endpoint that returns something other than a
        `ResultList` should override this method as required.
        """
        return self.api_result.total_count

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        data = super().get_datalayer_data(request)
        if self.form.cleaned_data.get("group"):
            custom_dimension8 = (
                self.search_tab + ": " + self.form.cleaned_data.get("group")
            )
        else:
            custom_dimension8 = self.search_tab + ": " + "none"

        custom_dimension9 = self.query or "*"

        result_count = self.get_result_count()

        data.update(
            customDimension8=custom_dimension8,
            customDimension9=custom_dimension9,
            # Value is capped to improve reporting reliability
            customMetric1=result_count if result_count < 10000 else 10000,
        )
        return data

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs["page_type"] = self.page_type
        kwargs["page_title"] = self.page_title
        return super().get_context_data(
            meta_title=self.get_meta_title(),
            search_query=self.query,
            result_count=self.get_result_count(),
            bucketkeys=BucketKeys,
            searchtabs=SearchTabs,
            vis_view=VisViews,
            timeline_type=TimelineTypes,
            display=Display,
            closure_closed_status=CLOSURE_CLOSED_STATUS,
            **kwargs,
        )

    def set_session_info(self) -> None:
        """
        Usually called where there are links to the record details page in the search results.
        Sets session in order for it to be used in record details page when navigating from search results.
        """

        self.request.session["back_to_search_url"] = self.request.get_full_path()
        self.request.session["back_to_search_url_timestamp"] = (
            timezone.now().isoformat()
        )
        return None


class BaseFilteredSearchView(BaseSearchView):
    """
    A more specialized version `BaseSearchView` that has additional features that
    only apply to a subset of views:

    *   Default form field values
    *   Pagination
    *   Dynamic choice fields: Form fields whose values are applied as
        'filter_aggregations' to the API request, then have their `choices`
        updated to reflect data in the response.
    """

    api_stream: str = ""
    api_method_name: str = ""

    default_group: str = ""
    default_per_page: int = 20
    default_sort: str = Sort.RELEVANCE.value
    default_display: str = Display.LIST.value
    default_view: str = VisViews.LIST.value

    dynamic_choice_fields = (
        "collection",
        "level",
        "topic",
        "closure",
        "held_by",
        "catalogue_source",
        "type",
        "country",
        "location",
        "place",
    )

    def get_initial(self) -> Dict[str, Any]:
        return {
            "group": self.default_group,
            "sort": self.default_sort,
            "per_page": self.default_per_page,
            "display": self.default_display,
            "vis_view": self.default_view,
        }

    @property
    def page_number(self) -> int:
        try:
            return int(self.request.GET["page"])
        except (ValueError, KeyError):
            return 1

    def form_invalid(self, form):
        """
        Interpret some form field errors as critical errors, returning a
        400 (Bad Request) response.
        """
        for field_name in (
            "group",
            "per_page",
            "sort",
            "display",
            "view",
        ):
            if field_name in form.errors:
                return HttpResponseBadRequest(str(form.errors[field_name]))

        # initialise empty result for an invalid form
        self.api_result = records_client.resultlist_from_response(
            response_data={}, bucket_counts=[]
        )

        return super().form_invalid(form)

    def get_api_kwargs(self, form: Form) -> Dict[str, Any]:
        page_size = form.cleaned_data.get("per_page")
        return dict(
            stream=self.api_stream,
            q=self.query or None,
            group=form.cleaned_data.get("group"),
            aggregations=self.get_api_aggregations(),
            filter_aggregations=self.get_api_filter_aggregations(form),
            filter_keyword=form.cleaned_data.get("filter_keyword"),
            opening_start_date=form.cleaned_data.get("opening_start_date"),
            opening_end_date=form.cleaned_data.get("opening_end_date"),
            created_start_date=form.cleaned_data.get("covering_date_from"),
            created_end_date=form.cleaned_data.get("covering_date_to"),
            offset=(self.page_number - 1) * page_size,
            size=page_size,
            sort=form.cleaned_data.get("sort"),
        )

    def get_api_aggregations(self) -> List[str]:
        """
        Called by `get_api_kwargs()` to get a value to include as 'aggregations'
        in the API request.

        The aggregations params may be specific to a bucket and will be filtered upon.
        Returns a list of aggregation params for the current bucket.
        Ex: ["group:30", "catalogue:10",]
        """
        return self.current_bucket.aggregations_normalised

    def get_api_filter_aggregations(self, form: Form) -> List[str]:
        """
        Called by `get_api_kwargs()` to get a value to include as
        'fitler_aggregations' in the API request.

        This is where values from the form are used to customise the API
        request.

        The API expects filter values to be supplied in a certain way: as a
        list of strings prefixed with the API field name. This function takes
        care of matching up form fields to the relevant API field name, and
        returning a list of filter strings that the API will understand.
        """
        filter_aggregations = []
        for field_name in self.dynamic_choice_fields:
            filter_name = underscore_to_camelcase(field_name)
            value = form.cleaned_data.get(field_name)
            filter_aggregations.extend((f"{filter_name}:{v}" for v in value))

        # The 'group' value is added separately, as the field is not a
        # MultipleChoiceField like the others
        filter_aggregations.append(f"group:{form.cleaned_data['group']}")
        return filter_aggregations

    def process_api_result(self, form: Form, api_result: Any):
        """
        Update `choices` values on the form's `dynamic_choice_fields` to
        reflect data included in the API's 'filter_aggregations' response.

        See also: `get_api_aggregations()`.
        """
        for value in api_result.aggregations:
            key = value.get("name")
            field_name = camelcase_to_underscore(key)
            if field_name in self.dynamic_choice_fields:
                choice_data = value.get("entries", ())
                form.fields[field_name].update_choices(
                    choice_data, selected_values=form.cleaned_data.get(field_name, ())
                )
                form[field_name].more_filter_options_available = bool(
                    value.get("docCount", 0)
                )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["selected_filters"] = self.get_selected_filters(self.form)
        self.selected_filters_count = context["selected_filters_count"] = sum(
            map(len, context["selected_filters"].values())
        )

        if self.api_result:
            paginator, page, page_range = self.paginate_api_result(
                result_list=self.api_result.hits,
                per_page=self.form.cleaned_data["per_page"],
                total_count=self.api_result.total_count,
            )
            context.update(
                paginator=paginator,
                page=page,
                page_range=page_range,
            )
        return context

    def get_selected_filters(self, form: Form) -> Dict[str, List[Tuple[str, str]]]:
        """
        Returns a dictionary of selected filters, keyed by form field name.
        Each value is a series of tuples where the first item is the 'value', and
        the second a user-freindly 'label' suitable for display in the template.
        """
        return_value = {
            field_name: form.cleaned_data[field_name]
            for field_name in self.dynamic_choice_fields
            if form.cleaned_data.get(field_name)
        }

        # Replace field 'values' with (value, label) tuples,
        # allowing both to be used in the template
        for field_name in return_value:
            field = form.fields[field_name]
            if field.configured_choice_labels:
                choice_labels = field.configured_choice_labels
            elif field.choices_updated:
                # Remove counts from the end of updated choice labels
                choice_labels = {
                    value: re.sub(r" \([0-9\,]+\)$", "", label, 0)
                    for value, label in field.choices
                }
            else:
                choice_labels = {value: label for value, label in field.choices}
            return_value[field_name] = [
                (value, choice_labels.get(value, value))
                for value in return_value[field_name]
            ]

        if filter_keyword := form.cleaned_data.get("filter_keyword"):
            return_value.update({"filter_keyword": [(filter_keyword, filter_keyword)]})

        if opening_start_date := form.cleaned_data.get("opening_start_date"):
            return_value["opening_start_date"] = [
                (
                    opening_start_date,
                    "Record opening from: " + opening_start_date.strftime("%d %m %Y"),
                )
            ]

        if opening_end_date := form.cleaned_data.get("opening_end_date"):
            return_value["opening_end_date"] = [
                (
                    opening_end_date,
                    "Record opening to: " + opening_end_date.strftime("%d %m %Y"),
                )
            ]

        if covering_date_from := form.cleaned_data.get("covering_date_from"):
            return_value["covering_date_from"] = [
                (
                    covering_date_from,
                    "Date from: " + covering_date_from.strftime("%d %m %Y"),
                )
            ]

        if covering_date_to := form.cleaned_data.get("covering_date_to"):
            return_value["covering_date_to"] = [
                (
                    covering_date_to,
                    "Date to: " + covering_date_to.strftime("%d %m %Y"),
                )
            ]

        return return_value

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        """
        Overrides BaseSearchView.get_datalayer_data() to include the number
        of filters selected by the user as 'customMetric2'.
        """
        data = super().get_datalayer_data(request)
        data.update(customMetric2=self.selected_filters_count)
        return data


class BaseLongFilterOptionsView(BaseFilteredSearchView):
    """
    A more specialized version `BaseFilteredSearchView` for long filters that has methods that
    only apply to a subset of views:
    """

    def get_meta_title(self) -> str:
        return f'Filter options for "{self.form_field.label}"'

    def get(self, request: HttpRequest, field_name: str) -> HttpResponse:
        """
        Handle GET requests: instantiate a form instance using
        request.GET as the data, then check if it's valid.
        """
        self.form = form = self.get_form()
        if field_name not in self.dynamic_choice_fields:
            raise Http404(
                f"'{field_name}' is not a valid field name. The value must be "
                f"one of: {self.dynamic_choice_fields}."
            )
        self.field_name = field_name
        self.bound_field = form[field_name]
        self.form_field = self.bound_field.field
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_api_aggregations(self) -> List[str]:
        """
        Overrides get_api_aggregations() to only request
        aggregations for the form field that options have been requested for.
        """
        aggregation_name = underscore_to_camelcase(self.field_name)
        return [f"{aggregation_name}:100"]

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs.update(
            field_name=self.field_name,
            bound_field=self.bound_field,
            field=self.form_field,
        )
        return super().get_context_data(**kwargs)


class CatalogueSearchView(BucketsMixin, BaseFilteredSearchView):
    api_method_name = "search"
    api_stream = Stream.EVIDENTIAL
    bucket_list = CATALOGUE_BUCKETS
    default_group = BucketKeys.COMMUNITY
    form_class = CatalogueSearchForm
    template_name = "search/catalogue_search.html"
    search_tab = SearchTabs.CATALOGUE.value
    page_type = "Catalogue search page"
    page_title = "Catalogue search"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        self.set_session_info()
        module = importlib.import_module("etna.search.common")

        kwargs.update(
            default_geo_data={
                "lat": settings.FEATURE_GEO_LAT,
                "lon": settings.FEATURE_GEO_LON,
                "zoom": settings.FEATURE_GEO_ZOOM,
            },
            list_view_url=module.VIS_URLS.get(VisViews.LIST.value),
            map_view_url=module.VIS_URLS.get(VisViews.MAP.value),
            timeline_view_url=module.VIS_URLS.get(VisViews.TIMELINE.value),
            tag_view_url=module.VIS_URLS.get(VisViews.TAG.value),
        )
        return super().get_context_data(**kwargs)


class CatalogueSearchLongFilterView(BaseLongFilterOptionsView):
    api_method_name = "search"
    api_stream = Stream.EVIDENTIAL
    default_group = BucketKeys.COMMUNITY
    form_class = CatalogueSearchForm
    template_name = "search/long_filter_options.html"
    page_type = "Catalogue search long filter page"
    page_title = "Catalogue search long filter"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(url_name="search-catalogue", **kwargs)
