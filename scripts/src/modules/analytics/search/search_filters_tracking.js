import push_to_data_layer from "./../push_to_data_layer";


const pushActiveFilterDataOnLoad = () => {
    // get filters after DOM has loaded and they have rendered on page
    window.addEventListener('load', () => {
        const filterList = document.querySelector('.search-results__selected-filters')
        if(filterList !== null) {
            pushActiveFilterData(filterList);
        }
    });
}

const pushActiveFilterData = (filterList) => {
    // get current search bucket
    const searchBucket = filterList.getAttribute('data-search-bucket');

    const filters = filterList.querySelectorAll("[data-filter]");

    // create array to store currently active filters
    const activeFilters = [];

    // loop through all currently active filters
    filters.forEach((filter) => {
        let value = filter.getAttribute('data-filter-value');
        const name = filter.getAttribute('data-filter-name');

        // if filter is a start or end date, set its value to 'Yes'
        if (name === 'opening_start_date' || name === 'opening_end_date') {
            value = 'Yes';
        }

        // setup the dataLayer variables for each filter
        let filterData = {
            'event': 'search-filters',
            'search_bucket': searchBucket || '',
            'search_filter_name': name || '',
            'search_filter_value': value || '',
        };

        // add currently active filters to activeFilters array
        activeFilters.push(filterData);
    });

    // check if start and end date filters are active (do they already exist in array?)
    let startDate = activeFilters.some(e => e.search_filter_name === 'opening_start_date');
    let endDate = activeFilters.some(e => e.search_filter_name === 'opening_end_date');

    // if startDate isn't active but endDate is, create a custom object with the value 'No'
    /*
    if (!startDate && endDate) {
        startDate = {
            'event': 'search-filters',
            'search_bucket': searchBucket || '',
            'search_filter_name': 'opening_start_date',
            'search_filter_value': 'No',
        };

        activeFilters.push(startDate);
    }
    

    // if endDate isn't active but startDate, create a custom object with the value 'No'
    if (!endDate && startDate) {
        endDate = {
            'event': 'search-filters',
            'search_bucket': searchBucket || '',
            'search_filter_name': 'opening_end_date',
            'search_filter_value': 'No',
        };

        activeFilters.push(endDate);
    }
    */
    if (!startDate && !endDate) {
        // if neither startDate nor endDate are present, do nothing;
    }

    // loop through the updated filters array and send each item to the dataLayer
    activeFilters.forEach((filter) => {
        push_to_data_layer(filter);
    });
}

export default pushActiveFilterDataOnLoad;
