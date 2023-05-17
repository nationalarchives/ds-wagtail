import push_to_data_layer from "./../push_to_data_layer";

const getSortBy = () => {
    // get filters after DOM has loaded and they have rendered on page
    window.addEventListener('load', () => {
        const sortBy = document.querySelector('[data-id="sort-form"]');
        const searchType = sortBy.getAttribute('data-search-type');
        const searchBucket = sortBy.getAttribute('data-search-bucket');
        const searchName = sortBy.getAttribute('data-search-filter-name');
        const searchValue = sortBy.getAttribute('data-search-filter-value');

        sortBy.addEventListener('submit', (e) => {
            e.preventDefault();

            let filterData = {
                'event_type': 'sort-results',
                'search_type': searchType || '',
                'search_bucket': searchBucket || '',
                'search_filter_name': searchName || '',
                'search_filter_value': searchValue || 'relevance',
            };

            push_to_data_layer(filterData);

            sortBy.submit();
        });
    });
}

const searchSortFiltersTracking = () => {
    getSortBy();
};

export default searchSortFiltersTracking;