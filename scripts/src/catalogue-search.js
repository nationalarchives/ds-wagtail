import mobileFilterExpander from "./modules/search/mobile-filter-expander-enhanced.js";
import searchBucketsExpander from "./modules/search/search-buckets-expander.js";
import searchLongFilters from "./modules/search/search-long-filters";
import longFiltersTracking from "./modules/analytics/search/long_filters_tracking";
import intialiseSearchResultTracking from "./modules/analytics/search/search_result_interaction";
import searchSortFiltersTracking from "./modules/analytics/search/search_sort_filters_tracking";
import pushActiveFilterDataOnLoad from "./modules/analytics/search/search_filters_tracking";
import pushActiveErrorsOnLoad from "./modules/analytics/search/search_errors_tracking";

mobileFilterExpander();
searchBucketsExpander();
searchLongFilters();
intialiseSearchResultTracking();
searchSortFiltersTracking();
pushActiveFilterDataOnLoad();
longFiltersTracking();
pushActiveErrorsOnLoad();
