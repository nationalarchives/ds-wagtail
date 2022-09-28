import copy
import logging
import re

from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple, Union
from urllib.parse import urlparse

from django.core.paginator import Page
from django.forms import Form
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.views.generic import FormView, TemplateView

from wagtail.coreutils import camelcase_to_underscore

from ..analytics.mixins import SearchDataLayerMixin
from ..ciim.client import Aggregation, SortBy, SortOrder, Stream, Template
from ..ciim.constants import (
    CATALOGUE_BUCKETS,
    FEATURED_BUCKETS,
    WEBSITE_BUCKETS,
    Bucket,
    BucketKeys,
    BucketList,
    Display,
    SearchTabs,
)
from ..ciim.paginator import APIPaginator
from ..ciim.utils import underscore_to_camelcase
from ..collections.models import ResultsPage
from ..insights.models import InsightsPage
from ..records.models import Record
from .forms import CatalogueSearchForm, FeaturedSearchForm, WebsiteSearchForm

logger = logging.getLogger(__name__)


class BucketsMixin:
    """
    A mixin for views that display a list of 'buckets' to a user.

    The `bucket_list` attribute should be set to one of the `BucketList`
    values from `etna.ciim.constants`. This value is copied and enhanced
    in the `get_buckets()` method to make the value more useful for
    rendering, then added to the template context as "buckets" by
    `get_context_data()`
    """

    # The source data for get_buckets()
    bucket_list: BucketList = None
    # Can be updated by the view for get_current_bucket_key() to pick up
    current_bucket_key: str = None

    def extract_group_buckets(
        self, api_result: Union[None, Dict[str, Any]]
    ) -> Sequence[Dict[str, Union[str, int]]]:
        """
        Attempts to find and return a list or values from `api_result`
        that can be passed to `get_buckets()`, allowing it to set the
        `result_count` value for each bucket.
        """
        if not api_result:
            return ()

        # Account for different API response structures
        aggregations = {}
        if api_result.get("responses"):
            aggregations = api_result["responses"][0].get("aggregations", {})
        else:
            aggregations = api_result.get("aggregations", {})

        # The API response has an unfamiliar structure
        if not aggregations:
            return ()

        return aggregations.get("group", {}).get("buckets", ())

    def get_current_bucket_key(self):
        return self.current_bucket_key

    def get_buckets(
        self,
        group_buckets: List[Dict[str, Union[str, int]]] = None,
        current_bucket_key: str = None,
    ) -> Optional[BucketList]:
        """
        Returns a modified `BucketList` value representing the 'buckets'
        that are available for the user to explore.

        If `group_buckets` is provided, the data will be used to set the `result_count`
        attribute for each bucket.

        The `current_bucket_key` is provided, any bucket with a `key` value matching
        the provided value will have it's `is_current` value set to `True`.
        """
        if not self.bucket_list:
            return None

        bucket_list = copy.deepcopy(self.bucket_list)

        if group_buckets:
            # set `result_count` for each bucket
            doc_counts_by_key = {
                group["key"]: group["doc_count"] for group in group_buckets
            }
            for bucket in bucket_list:
                bucket.result_count = doc_counts_by_key.get(bucket.key, 0)

        if current_bucket_key:
            # set 'is_current=True' for the relevant bucket
            for bucket in bucket_list:
                if bucket.key == current_bucket_key:
                    bucket.is_current = True
                    break

        return bucket_list

    def get_context_data(self, **kwargs):
        if self.bucket_list:
            group_buckets = self.extract_group_buckets(
                getattr(self, "api_result", None)
            )
            current_bucket_key = self.get_current_bucket_key()
            kwargs["buckets"] = self.get_buckets(group_buckets, current_bucket_key)
        return super().get_context_data(**kwargs)


class KongAPIMixin:
    """
    A mixin for views that call the Kong API to retrieve and display
    records.
    """

    # The name of the method on the API client to request from
    api_method_name: str = ""

    def get_api_result(self, form: Form) -> Dict[str, Any]:
        """
        Queries the API, and returns a `dict` containing any data from the
        response that is useful for the request.
        """
        client = Record.api.client
        # variabalize the method for calling below
        client_method_to_call = getattr(client, self.api_method_name)
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
    ) -> Tuple[APIPaginator, Page, Iterator[int]]:
        """
        Returns pagination-related objects to facilitate rendering of
        pagination links etc. The correct page of results should have
        already been fetched from the API by this point, so the paginator
        has no impact on the results that are displayed.
        """
        paginator = APIPaginator(total_count, per_page=per_page)
        page = Page(result_list, number=self.page_number, paginator=paginator)
        page_range = paginator.get_elided_page_range(number=self.page_number, on_ends=0)
        return paginator, page, page_range


class SearchLandingView(SearchDataLayerMixin, BucketsMixin, TemplateView):
    """
    A simple view that queries the API to retrieve counts for the various
    buckets the user can explore, and provides a form to encourage the user
    to dig deeper. Any interaction should take them to one of the other,
    more sophisticated, views below.

    Although this view called the Kong API, it does not use KongAPIMixin,
    as the unique functionality is simple enough to keep in a single method.
    """

    template_name = "search/search.html"
    bucket_list = CATALOGUE_BUCKETS

    def get_context_data(self, **kwargs):
        # Make empty search to fetch aggregations
        self.api_result = Record.api.client.search(
            template=Template.DETAILS,
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
        return super().get_context_data(
            meta_title="Search the collection",
            form=CatalogueSearchForm(),
            **kwargs,
        )


class BaseSearchView(SearchDataLayerMixin, KongAPIMixin, FormView):
    """
    A base view that uses a Django form to interpret/clean querystring
    data, then uses those values to make an API request and render
    results to a template.

    To learn more about FormView, see:
    * https://docs.djangoproject.com/en/3.2/topics/class-based-views/generic-editing/
    * https://ccbv.co.uk/projects/Django/3.2/django.views.generic.edit/FormView/
    """

    base_title = "Search results"

    http_method_names = ["get", "head"]

    def get(self, request: HttpRequest, **kwargs: Any) -> HttpResponse:
        """
        Handle GET requests: instantiate a form instance using
        request.GET as the data, then check if it's valid.
        """
        form = self.form = self.get_form()
        is_valid = form.is_valid()
        self.api_result = None
        self.current_bucket_key = form.cleaned_data.get("group")
        if is_valid:
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_form_kwargs(self) -> Dict[str, Any]:
        """
        Overrides FormView.get_form_kwargs() to use `request.GET` for data
        instead `request.POST`. Thes values are used by FormView.get_form()
        to initialise the form object used by the view.
        """
        kwargs = super().get_form_kwargs()
        data = self.request.GET.copy()
        for k, v in self.get_form_defaults().items():
            data.setdefault(k, v)
        kwargs["data"] = data
        return kwargs

    def get_form_defaults(self) -> Dict[str, Any]:
        """
        Form views have a `get_initial()` method to set initial values on form
        fields, but because we're ALWAYS providing GET data to the form, those
        initial values are always overriden. To make up for this,
        get_form_kwargs() mixes this method's return value into the GET data
        where no value has been specified, so that the data makes it into the
        form.
        """
        return {}

    def form_valid(self, form: Form) -> HttpResponse:
        """
        When the form is valid, fetch results from the API, take any actions
        based on the result, then render everything to a template.
        """
        self.api_result = api_result = self.get_api_result(form)
        self.process_api_result(form, api_result)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_meta_title(self) -> str:
        """
        Return a string to use the the <title> tag for this view.
        """
        title = self.base_title
        if query := self.form.cleaned_data.get("q", ""):
            title += ' for "' + query.replace('"', "'") + '"'
        return title

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        data = super().get_datalayer_data(request)
        if self.form.cleaned_data.get("group"):
            custom_dimension8 = (
                self.title_base + ": " + self.form.cleaned_data.get("group")
            )
        else:
            custom_dimension8 = self.title_base + ": " + "none"
        custom_dimension9 = self.form.cleaned_data.get("q") or "*"
        try:
            custom_metric2 = len(self.get_api_filter_aggregations(self.form)) - 1
        except AttributeError:  # This is needed as it will throw an error as some pages do not have filters (e.g. Featured Search, or Record Creator bucket)
            custom_metric2 = 0
        data.update(
            customDimension8=custom_dimension8,
            customDimension9=custom_dimension9,
            customMetric2=custom_metric2,
        )
        return data

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs.update(
            meta_title=self.get_meta_title(),
            search_query=self.form.cleaned_data.get("q", ""),
        )
        return super().get_context_data(**kwargs)


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
    default_sort_by: str = SortBy.RELEVANCE.value
    default_sort_order: str = SortOrder.ASC.value
    default_display: str = Display.LIST.value

    dynamic_choice_fields = (
        "collection",
        "level",
        "topic",
        "closure",
        "held_by",
        "catalogue_source",
        "type",
    )

    def get_form_defaults(self) -> Dict[str, Any]:
        return {
            "group": self.default_group,
            "sort_by": self.default_sort_by,
            "sort_order": self.default_sort_order,
            "per_page": self.default_per_page,
            "display": self.default_display,
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
            "sort_by",
            "sort_order",
            "display",
        ):
            if field_name in form.errors:
                return HttpResponseBadRequest(str(form.errors[field_name]))

        return super().form_invalid(form)

    def get_api_kwargs(self, form: Form) -> Dict[str, Any]:
        page_size = form.cleaned_data.get("per_page")
        opening_start_date = form.cleaned_data.get("opening_start_date")
        opening_end_date = form.cleaned_data.get("opening_end_date")
        return dict(
            stream=self.api_stream,
            q=form.cleaned_data.get("q"),
            aggregations=self.get_api_aggregations(),
            filter_aggregations=self.get_api_filter_aggregations(form),
            filter_keyword=form.cleaned_data.get("filter_keyword"),
            opening_start_date=opening_start_date,
            opening_end_date=opening_end_date,
            offset=(self.page_number - 1) * page_size,
            size=page_size,
            template=Template.DETAILS,
            sort_by=form.cleaned_data.get("sort_by"),
            sort_order=form.cleaned_data.get("sort_order"),
        )

    def get_api_aggregations(self) -> List[str]:
        """
        Called by `get_api_kwargs()` to get a value to include as 'aggregations'
        in the API request.

        In the API response, the items with the highest number of matches are
        included for each aggregation. Those values are used to indicate
        counts for each 'bucket', and to update the form field choices, so that
        the most relevant filter options are shown.
        """
        values = []
        for aggregation in (
            Aggregation.COLLECTION,
            Aggregation.LEVEL,
            Aggregation.TOPIC,
            Aggregation.CLOSURE,
            Aggregation.HELD_BY,
            Aggregation.CATALOGUE_SOURCE,
            Aggregation.GROUP,
            Aggregation.TYPE,
        ):
            item_count = 10
            if aggregation == Aggregation.GROUP:
                # Fetch more 'groups' so that we receive a counts
                # for any bucket/tab options we might be showing
                # (not just the 10 most popular)
                item_count = 30
            values.append(f"{aggregation}:{item_count}")
        return values

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

    def process_api_result(self, form: Form, api_result: Dict[str, Any]):
        """
        Update the `choices` value on the form's `dynamic_choice_fields` to
        reflect the 'aggregations' data included in the API response.

        See also: `get_api_aggregations()`.
        """
        aggregations = api_result["responses"][1].get("aggregations", {})
        for key, value in aggregations.items():
            if buckets := value.get("buckets"):
                field_name = camelcase_to_underscore(key)
                if field_name in self.dynamic_choice_fields:
                    form.fields[field_name].update_choices(buckets)
                    form[field_name].more_filter_options_available = bool(
                        value.get("sum_other_doc_count", 0)
                    )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["selected_filters"] = self.get_selected_filters(self.form)
        if self.api_result:
            result_response = self.api_result["responses"][1]
            total_count = result_response["hits"]["total"]["value"]
            per_page = self.form.cleaned_data["per_page"]
            paginator, page, page_range = self.paginate_api_result(
                result_list=result_response["hits"]["hits"],
                per_page=per_page,
                total_count=total_count,
            )
            context.update(
                paginator=paginator,
                page=page,
                page_range=page_range,
            )
        return context

    def get_selected_filters(self, form: Form) -> Dict[str, List[Tuple[str, str]]]:
        """Returns a list of selected dynamic_choice_fields values, keyed by
        the corresponding field name.

        Used by template to output a list of selected filters.
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
        return return_value


class CatalogueSearchView(BucketsMixin, BaseFilteredSearchView):
    api_method_name = "search"
    api_stream = Stream.EVIDENTIAL
    bucket_list = CATALOGUE_BUCKETS
    default_group = "tna"
    form_class = CatalogueSearchForm
    template_name = "search/catalogue_search.html"
    title_base = SearchTabs.CATALOGUE.value

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        data = super().get_datalayer_data(request)
        total_count = 0
        if self.api_result:
            # a respose is returned for valid input
            if aggregations := self.api_result["responses"][1].get("aggregations"):
                for bucket in aggregations["catalogueSource"]["buckets"]:
                    total_count += bucket["doc_count"]
        if total_count > 10000:
            total_count = 10001
        data.update(customMetric1=total_count)
        return data

    def get_context_data(self, **kwargs):
        kwargs["bucketkeys"] = BucketKeys
        kwargs["searchtabs"] = SearchTabs
        return super().get_context_data(**kwargs)


class CatalogueSearchLongFilterView(BaseFilteredSearchView):
    api_method_name = "search"
    api_stream = Stream.EVIDENTIAL
    default_group = "tna"
    form_class = CatalogueSearchForm
    template_name = "search/catalogue_search_long_filter_chooser.html"

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
        Overrides CatalogueSearchView.get_api_aggregations() to only request
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


class WebsiteSearchView(BucketsMixin, BaseFilteredSearchView):
    api_stream = Stream.INTERPRETIVE
    api_method_name = "search"
    bucket_list = WEBSITE_BUCKETS
    default_group = "blog"
    form_class = WebsiteSearchForm
    template_name = "search/website_search.html"
    title_base = SearchTabs.WEBSITE.value

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        data = super().get_datalayer_data(request)
        total_count = self.api_result["responses"][1]["hits"]["total"]["value"]
        if total_count > 10000:
            total_count = 10001
        data.update(customMetric1=total_count)
        return data

    def add_insights_page_for_url(self, page: Page) -> None:
        """
        Finds the Insights page corresponding to the sourceUrl of a record, then adds that page to result of the same record.
        Unmatched url is bypassed but logged.
        """
        slugs = [
            result["_source"]
            .get("@template", {})
            .get("details", {})
            .get("sourceUrl", "")
            .rstrip("/")
            .split("/")
            .pop()
            for result in page.object_list
        ]
        # filter by slug for performance boost
        insights_page_by_url = {
            page.get_url(self.request): page
            for page in InsightsPage.objects.live()
            .filter(slug__in=slugs)
            .defer("body")
            .select_related("teaser_image")
        }
        page_list = []
        for result in page.object_list:
            url = (
                result["_source"]
                .get("@template", {})
                .get("details", {})
                .get("sourceUrl", "")
            )
            if source_page := insights_page_by_url.get(urlparse(url).path, ""):
                result["source_page"] = source_page
            else:
                logger.debug(
                    f"WebsiteSearchView:scrapped/ingested url={url} not found in insights_page_by_url={insights_page_by_url}"
                )
            page_list.append(result)
        page.object_list = page_list

    def add_results_page_for_url(self, page: Page) -> None:
        """
        Finds the Results page corresponding to the sourceUrl of a record, then adds that page to result of the same record.
        Unmatched url is bypassed but logged.
        """
        slugs = [
            result["_source"]
            .get("@template", {})
            .get("details", {})
            .get("sourceUrl", "")
            .rstrip("/")
            .split("/")
            .pop()
            for result in page.object_list
        ]
        results_page_by_url = {
            page.get_url(self.request): page
            for page in ResultsPage.objects.live()
            .filter(slug__in=slugs)
            .select_related("teaser_image")
        }
        page_list = []
        for result in page.object_list:
            url = (
                result["_source"]
                .get("@template", {})
                .get("details", {})
                .get("sourceUrl", "")
            )
            if source_page := results_page_by_url.get(urlparse(url).path, ""):
                result["source_page"] = source_page
            else:
                logger.debug(
                    f"WebsiteSearchView:scrapped/ingested url={url} not found in results_page_by_url={results_page_by_url}"
                )
            page_list.append(result)
        page.object_list = page_list

    def get_context_data(self, **kwargs):
        kwargs["bucketkeys"] = BucketKeys
        context = super().get_context_data(**kwargs)
        if filter_aggregation := self.request.GET.get("group", ""):
            if filter_aggregation == "insight" and "page" in context:
                self.add_insights_page_for_url(context["page"])
            if filter_aggregation == "highlight" and "page" in context:
                self.add_results_page_for_url(context["page"])
        return context


class FeaturedSearchView(BaseSearchView):
    api_method_name = "search_all"
    form_class = FeaturedSearchForm
    template_name = "search/featured_search.html"
    title_base = SearchTabs.ALL.value
    featured_search_total_count = 0

    def get_api_kwargs(self, form: Form) -> Dict[str, Any]:
        return {
            "q": form.cleaned_data.get("q"),
            "filter_aggregations": [
                f"group:{bucket.key}" for bucket in FEATURED_BUCKETS
            ],
            "size": 3,
        }

    def get_buckets(self) -> Dict[str, Bucket]:
        """
        This method is similar in principal to `BucketMixin.get_buckets()`,
        but to support template/rendering needs, it returns a `dict` instead of
        a `BucketList`, and instead of receiving additional argument values,
        `result_count` and `results` are set on each bucket using data
        directly from `self.api_result`.
        """
        buckets = {}
        for i, bucket in enumerate(copy.deepcopy(FEATURED_BUCKETS)):
            response = self.api_result["responses"][i]
            bucket.result_count = response["hits"]["total"]["value"]
            bucket.results = response["hits"]["hits"]
            buckets[bucket.key] = bucket
            self.featured_search_total_count += bucket.result_count
        return buckets

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        data = super().get_datalayer_data(request)
        total_count = self.featured_search_total_count
        if total_count > 10000:
            total_count = 10001
        data.update(customMetric1=total_count)
        return data

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(buckets=self.get_buckets(), **kwargs)
