import push_to_data_layer from "./../push_to_data_layer";

const getSortBy = () => {
    
    
    // get filters after DOM has loaded and they have rendered on page
    window.addEventListener('load', () => {
        const selectElement = document.querySelector('#id_sort_by');

        // check if selectElement exists to avoid errors on other search pages
        if (selectElement) {
            const selectOutput = selectElement.options[selectElement.selectedIndex].value.trim();

            const sortBy = document.querySelector('[data-id="sort-form"]');
            sortBy.setAttribute("data-search-filter-value", selectOutput);

            selectElement.onchange = function() {
                let selectOutput = this.options[this.selectedIndex].value.trim();
        
                sortBy.setAttribute("data-search-filter-value", selectOutput);
            }

            const searchType = sortBy.getAttribute('data-search-type');
            const searchBucket = sortBy.getAttribute('data-search-bucket');

            sortBy.addEventListener('submit', (e) => {
                e.preventDefault();

                let searchName = sortBy.getAttribute('data-search-filter-name');
                let searchValue = sortBy.getAttribute('data-search-filter-value');

                let filterData = {
                    'event': 'sort-results',
                    'search_type': searchType || '',
                    'search_bucket': searchBucket || '',
                    'search_filter_name': searchName || '',
                    'search_filter_value': searchValue || 'relevance',
                };

                push_to_data_layer(filterData);

                sortBy.submit();
            });
        }
    });
}

const searchSortFiltersTracking = () => {
    getSortBy();
};

export default searchSortFiltersTracking;