import copy
import importlib
import logging
import re

from datetime import date
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

from django.conf import settings
from django.core.paginator import Page as PaginatorPage
from django.forms import Form
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from django.views.generic import FormView, TemplateView

from wagtail.coreutils import camelcase_to_underscore

from ..analytics.mixins import SearchDataLayerMixin
from ..ciim.client import Aggregation, Sort
from ..ciim.constants import (
    AGGS_LOOKUP_KEY,
    CATALOGUE_BUCKETS,
    CHILD_AGGS_PREFIX,
    CLOSURE_CLOSED_STATUS,
    COLLECTION_ATTR_FOR_ALL_BUCKETS,
    LONG_AGGS_PREFIX,
    NESTED_CHECKBOX_VALUES_AGGS_NAMES_MAP,
    NESTED_CHILDREN_KEY,
    OHOS_CHECKBOX_AGGS_NAME_MAP,
    PARENT_AGGS_PREFIX,
    PREFIX_AGGS_PARENT_CHILD_KV,
    PREFIX_FILTER_AGGS,
    SEE_MORE_VALUE_FMT,
    TAG_VIEW_AGGREGATIONS,
    Bucket,
    BucketKeys,
    BucketList,
    Display,
    SearchTabs,
    TagTypes,
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
        bucket_counts_by_key = {
            entries["value"]: entries["count"] for entries in self.get_bucket_counts()
        }
        for bucket in bucket_list:
            bucket.result_count = bucket_counts_by_key.get(bucket.key, 0)

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
            tag_type=TagTypes,
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

    # api_stream: str = ""  # TODO: Keep, not in scope for Ohos-Etna at this time
    api_method_name: str = ""

    default_group: str = ""
    default_per_page: int = 20
    default_sort: str = Sort.RELEVANCE.value
    default_display: str = Display.LIST.value
    default_view: str = VisViews.LIST.value

    dynamic_choice_fields = (
        "collection",
        "chart_selected",
        # TODO: Keep, not in scope for Ohos-Etna at this time
        # "level",
        # "topic",
        # "closure",
        # "held_by",
        # "catalogue_source",
        # "type",
        # "country",
        # "location",
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
            # stream=self.api_stream,  # TODO: Keep, not in scope for Ohos-Etna at this time
            q=self.query or None,
            group=form.cleaned_data.get("group"),
            aggregations=self.get_api_aggregations(),
            filter_aggregations=self.get_api_filter_aggregations(form),
            # TODO: Keep, not in scope for Ohos-Etna at this time
            # filter_keyword=form.cleaned_data.get("filter_keyword"),
            # opening_start_date=form.cleaned_data.get("opening_start_date"),
            # opening_end_date=form.cleaned_data.get("opening_end_date"),
            covering_date_from=form.cleaned_data.get("covering_date_from"),
            covering_date_to=form.cleaned_data.get("covering_date_to"),
            offset=(self.page_number - 1) * page_size,
            size=page_size,
            sort=form.cleaned_data.get("sort"),
            vis_view=form.cleaned_data.get("vis_view"),
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

    def _prepare_see_more_choice(
        self, aggs_rec: Dict[str, Any], field_name: str
    ) -> Dict:
        """
        Prepares see more to be extracted as a choice and then url in template.
        aggs_rec:
            aggregations record in the API response ex "collectionMorrab"
        field_name:
            name of the checkbox field

        Ex:
        see_more_value=SEE-MORE::SEP::See more collections::SEP::
        /search/catalogue/long-filter-chooser/collection/
        ?collection=long-collectionMorrabAll%3AMorrab+Photo+Archive
        &collection=parent-collectionMorrab%3AMorrab+Photo+Archive&vis_view=list&group=community
        """
        choice_data = {}
        see_more_count = aggs_rec.get("other")  # attribute that determines see more
        if see_more_count > 0:
            long_filter_aggs = NESTED_CHECKBOX_VALUES_AGGS_NAMES_MAP.get(field_name)[1]

            data = f"{LONG_AGGS_PREFIX}{long_filter_aggs}:{field_name}"
            add_url_params = f"?{urlencode({COLLECTION_ATTR_FOR_ALL_BUCKETS:data})}"

            # add params to handle return to search
            fields_to_add = (
                "q",
                "sort",
                "collection",
                "covering_date_from",
                "covering_date_to",
                "vis_view",
                "group",
            )
            if self.form.cleaned_data.get("vis_view") == VisViews.TIMELINE:
                fields_to_add += ("timeline_type", "creation_date_from")

            for field, data in self.form.cleaned_data.items():
                if field in fields_to_add and data:
                    if isinstance(data, str):
                        add_url_params += f"&{urlencode({field:data})}"
                    elif isinstance(data, list):
                        for filter in data:
                            add_url_params += f"&{urlencode({field:filter})}"
                    elif isinstance(data, date):
                        date_params = {
                            f"{field}_0": str(data.day).zfill(2),
                            f"{field}_1": str(data.month).zfill(2),
                            f"{field}_2": str(data.year).zfill(4),
                        }
                        add_url_params += f"&{urlencode(date_params)}"
            url = reverse(
                "search-catalogue-long-filter-chooser",
                kwargs={"field_name": COLLECTION_ATTR_FOR_ALL_BUCKETS},
            )
            url += add_url_params
            see_more_value = SEE_MORE_VALUE_FMT.format(url=url)

            choice_data = {
                "value": see_more_value,
                "doc_count": see_more_count,
            }

        return choice_data

    def _transform_api_result_aggregations_for_nested_checkbox_collection(
        self, api_result: Any
    ):
        """
        Transforms the API aggregations for nested checkbox
        when the "other" count is more than 0 it indicates there are more collections
        see more is added to children - used as a url

        Ex:
        API aggregations:
        [{'name': 'collectionSurrey',
          'entries': [{'value': 'GYPSY ROMA TRAVELLER HISTORY MONTH: RECORDED INTERVIEWS', 'doc_count': 12}],
           'total': 17,
           'other': 22},
          {'name': 'community',
            'entries': [{'value': 'Surrey History Centre', 'doc_count': 17}],
            'total': 0,
            'other': 0}]
        Transformed aggregations:
        [{'name': 'collection',
          'entries': [{'value': 'Surrey History Centre',
                       'doc_count': 17,
                       'key': 'parent-collectionSurrey',
                       'children': [{'value': 'GYPSY ROMA TRAVELLER HISTORY MONTH: RECORDED INTERVIEWS',
                                     'doc_count': 12,
                                     'key': 'child-collectionSurrey'},
                                     ...
                                     {'value': 'See more collections', 'doc_count': 22}]}],
                                     'total': 0,
                                     'other': 0}]
        """
        remove_aggregations = []
        for index1, aggs_rec in enumerate(api_result.aggregations):
            aggs_name = aggs_rec.get("name")

            if aggs_name == OHOS_CHECKBOX_AGGS_NAME_MAP.get(
                COLLECTION_ATTR_FOR_ALL_BUCKETS
            ):
                # rename the aggregation to the form element name
                api_result.aggregations[index1].update(
                    name=COLLECTION_ATTR_FOR_ALL_BUCKETS
                )
                # add key for parent collections
                for index2, entry in enumerate(aggs_rec.get("entries", [])):
                    if collection_name := entry.get("value"):
                        if (
                            collection_name
                            in NESTED_CHECKBOX_VALUES_AGGS_NAMES_MAP.keys()
                        ):
                            nested_aggs_name = (
                                NESTED_CHECKBOX_VALUES_AGGS_NAMES_MAP.get(
                                    collection_name
                                )[0]
                            )
                            parent_aggs_name = PARENT_AGGS_PREFIX + nested_aggs_name
                            # add key for parent collections
                            api_result.aggregations[index1]["entries"][index2].update(
                                key=parent_aggs_name
                            )

                            child_aggs_name = PREFIX_AGGS_PARENT_CHILD_KV.get(
                                parent_aggs_name
                            )
                            children = []
                            for aggs_rec in api_result.aggregations:
                                if aggs_rec.get("name") == nested_aggs_name:
                                    remove_aggregations.append(nested_aggs_name)
                                    children = aggs_rec.get("entries")
                                    for index, child in enumerate(children):
                                        children[index].update(
                                            {AGGS_LOOKUP_KEY: child_aggs_name}
                                        )

                                    if see_more := self._prepare_see_more_choice(
                                        aggs_rec, collection_name
                                    ):
                                        children.append(see_more)

                            # add children KV
                            if children:
                                api_result.aggregations[index1]["entries"][
                                    index2
                                ].update({NESTED_CHILDREN_KEY: children})

        new_aggregations = [
            aggs_rec
            for aggs_rec in api_result.aggregations
            if aggs_rec.get("name") not in remove_aggregations
        ]
        api_result.aggregations = new_aggregations

    def process_api_result(self, form: Form, api_result: Any):
        """
        Update `choices` values on the form's `dynamic_choice_fields` to
        reflect data included in the API's 'filter_aggregations' response.

        See also: `get_api_aggregations()`.
        """
        if form.cleaned_data.get("group") == BucketKeys.COMMUNITY:
            self._transform_api_result_aggregations_for_nested_checkbox_collection(
                api_result
            )

        for value in api_result.aggregations:
            key = value.get("name")
            field_name = camelcase_to_underscore(key)
            if field_name in self.dynamic_choice_fields:
                choice_data = value.get("entries", ())
                form.fields[field_name].update_choices(
                    choice_data, selected_values=form.cleaned_data.get(field_name, ())
                )
                form[field_name].more_filter_options_available = bool(
                    value.get("other", 0)
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

        Exclude field names for Tag visualisation view
        """
        exclude_field_names = (
            ["chart_selected"]
            if form.cleaned_data.get("vis_view") == VisViews.TAG
            else []
        )

        return_value = {
            field_name: form.cleaned_data[field_name]
            for field_name in self.dynamic_choice_fields
            if form.cleaned_data.get(field_name)
            and field_name not in exclude_field_names
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

            if form.cleaned_data.get("group") == "community":
                # trims the filter labels for nested collections
                label_value_list = []
                for value in return_value[field_name]:
                    label = choice_labels.get(value, value)
                    if value.startswith(tuple(PREFIX_FILTER_AGGS)):
                        # remove prefix filter
                        label = value.split(":", 1)[1]
                    label_value_list.append((value, label))

                return_value[field_name] = label_value_list
            else:
                return_value[field_name] = [
                    (value, choice_labels.get(value, value))
                    for value in return_value[field_name]
                ]

        # TODO: Keep, not in scope for Ohos-Etna at this time
        # if filter_keyword := form.cleaned_data.get("filter_keyword"):
        #     return_value.update({"filter_keyword": [(filter_keyword, filter_keyword)]})

        # TODO: Keep, not in scope for Ohos-Etna at this time
        # if opening_start_date := form.cleaned_data.get("opening_start_date"):
        #     return_value["opening_start_date"] = [
        #         (
        #             opening_start_date,
        #             "Record opening from: " + opening_start_date.strftime("%d %m %Y"),
        #         )
        #     ]

        # TODO: Keep, not in scope for Ohos-Etna at this time
        # if opening_end_date := form.cleaned_data.get("opening_end_date"):
        #     return_value["opening_end_date"] = [
        #         (
        #             opening_end_date,
        #             "Record opening to: " + opening_end_date.strftime("%d %m %Y"),
        #         )
        #     ]

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

    def get_api_kwargs(self, form: Form) -> Dict[str, Any]:
        kwargs = super().get_api_kwargs(form)
        kwargs.update(long_filter=True)
        return kwargs

    def get_api_aggregations(self) -> List[str]:
        """
        Overrides get_api_aggregations() to only request
        aggregations for the form field that options have been requested for.
        """
        aggregation_name = underscore_to_camelcase(self.field_name)
        if self.form.cleaned_data.get("group") == BucketKeys.COMMUNITY.value:
            return super().get_api_aggregations()
        return [f"{aggregation_name}:100"]

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs.update(
            field_name=self.field_name,
            bound_field=self.bound_field,
            field=self.form_field,
        )
        return super().get_context_data(**kwargs)

    def process_api_result(self, form: Form, api_result: Any):

        remove_aggregations = []
        long_filter_aggs_map = dict(
            [
                (aggs[1], CHILD_AGGS_PREFIX + aggs[0])
                for aggs in NESTED_CHECKBOX_VALUES_AGGS_NAMES_MAP.values()
            ]
        )
        for index1, aggs_rec in enumerate(api_result.aggregations):
            aggs_name = aggs_rec.get("name")

            if aggs_name in long_filter_aggs_map.keys():
                # rename the aggregation to the form element name
                api_result.aggregations[index1].update(
                    name=COLLECTION_ATTR_FOR_ALL_BUCKETS
                )

                # get aggs for long filter aggs
                key = long_filter_aggs_map.get(aggs_name)

                # add child key for long filter
                for index2, _ in enumerate(aggs_rec.get("entries", [])):
                    api_result.aggregations[index1]["entries"][index2].update(key=key)
            else:
                remove_aggregations.append(aggs_name)

        new_aggregations = [
            aggs_rec
            for aggs_rec in api_result.aggregations
            if aggs_rec.get("name") not in remove_aggregations
        ]
        api_result.aggregations = new_aggregations

        selected_values = ()
        for value in api_result.aggregations:
            key = value.get("name")
            field_name = camelcase_to_underscore(key)
            if field_name in self.dynamic_choice_fields:
                choice_data = value.get("entries", ())
                form.fields[field_name].update_choices(
                    choice_data,
                    selected_values=selected_values,
                )
                form[field_name].more_filter_options_available = bool(
                    value.get("other", 0)
                )


class CatalogueSearchView(BucketsMixin, BaseFilteredSearchView):
    api_method_name = "search"
    # api_stream = Stream.EVIDENTIAL  # TODO: Keep, not in scope for Ohos-Etna at this time
    bucket_list = CATALOGUE_BUCKETS
    default_group = BucketKeys.COMMUNITY.value
    form_class = CatalogueSearchForm
    template_name = "search/catalogue_search.html"
    search_tab = SearchTabs.CATALOGUE.value
    page_type = "Catalogue search page"
    page_title = "Catalogue search"

    def _get_ohos_kwargs(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds template tags for OHOS visualisation links
        """
        # params to append to the visual links template tags
        fields_to_add = (
            "q",
            "sort",
            "collection",
            "covering_date_from",
            "covering_date_to",
        )

        module = importlib.import_module("etna.search.common")

        vis_view = self.form.cleaned_data.get("vis_view")

        if vis_view == VisViews.MAP:
            kwargs.update(
                default_geo_data={
                    "lat": settings.FEATURE_GEO_LAT,
                    "lon": settings.FEATURE_GEO_LON,
                    "zoom": settings.FEATURE_GEO_ZOOM,
                },
            )

        # update visualisation links with search and filters
        add_url_params = ""
        for field, data in self.form.cleaned_data.items():
            if field in fields_to_add and data:
                if isinstance(data, str):
                    add_url_params += f"&{urlencode({field:data})}"
                elif isinstance(data, list):
                    for item in data:
                        add_url_params += f"&{urlencode({field:item})}"
                elif isinstance(data, date):
                    date_params = {
                        f"{field}_0": str(data.day).zfill(2),
                        f"{field}_1": str(data.month).zfill(2),
                        f"{field}_2": str(data.year).zfill(4),
                    }
                    add_url_params += f"&{urlencode(date_params)}"

        kwargs.update(
            list_view_url=module.VIS_URLS.get(VisViews.LIST.value) + add_url_params,
            map_view_url=module.VIS_URLS.get(VisViews.MAP.value) + add_url_params,
            timeline_view_url=module.VIS_URLS.get(VisViews.TIMELINE.value)
            + add_url_params,
            tag_view_url=module.VIS_URLS.get(VisViews.TAG.value) + add_url_params,
        )

        vis_view = self.form.cleaned_data.get("vis_view")
        if vis_view == VisViews.TAG:
            for aggs_rec in self.api_result.aggregations:
                aggs = aggs_rec.get("name")
                if aggs == Aggregation.ENRICHMENT_LOC:
                    kwargs.update(enrichment_loc_aggs=aggs_rec.get("entries", []))
                elif aggs == Aggregation.ENRICHMENT_PER:
                    kwargs.update(enrichment_per_aggs=aggs_rec.get("entries", []))
                elif aggs == Aggregation.ENRICHMENT_ORG:
                    kwargs.update(enrichment_org_aggs=aggs_rec.get("entries", []))
                elif aggs == Aggregation.ENRICHMENT_MISC:
                    kwargs.update(enrichment_misc_aggs=aggs_rec.get("entries", []))

        return kwargs

    def get_api_aggregations(self) -> List[str]:
        """
        Overrides get_api_aggregations() to only request
        aggregations for the form field that options have been requested for.
        """
        if self.form.cleaned_data.get("vis_view") == VisViews.TAG.value:
            return TAG_VIEW_AGGREGATIONS
        return super().get_api_aggregations()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        self.set_session_info()

        if self.current_bucket_key == BucketKeys.COMMUNITY:
            add_kwargs = self._get_ohos_kwargs(**kwargs)
            kwargs.update(add_kwargs)

        return super().get_context_data(**kwargs)


class CatalogueSearchLongFilterView(BaseLongFilterOptionsView):
    api_method_name = "search"
    # api_stream = Stream.EVIDENTIAL  # TODO: Keep, not in scope for Ohos-Etna at this time
    bucket_list = CATALOGUE_BUCKETS
    default_group = BucketKeys.COMMUNITY.value
    form_class = CatalogueSearchForm
    template_name = "search/long_filter_options.html"
    page_type = "Catalogue search long filter page"
    page_title = "Catalogue search long filter"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(url_name="search-catalogue", **kwargs)
