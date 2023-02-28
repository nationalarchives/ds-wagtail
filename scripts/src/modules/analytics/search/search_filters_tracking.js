import push_to_data_layer from "./../push_to_data_layer";

const getFilters = () => {
    // get filters after DOM has loaded and they have rendered on page
    window.addEventListener('load', () => {
        const filters = document.querySelectorAll('[data-filter]');

        loopFilters(filters);
    });
}

const loopFilters = (filters) => {
    filters.forEach((filter) => {
        const bucket = filter.getAttribute('data-search-bucket');
        const value = filter.getAttribute('data-filter-value');
        const name = filter.getAttribute('data-filter-name');

        const filterData = {
            'search-bucket': bucket || '',
            'search-filter-value': value || '',
            'search-filter-name': name || '',
        }; 

        push_to_data_layer(filterData);

        console.log(filterData);
    });
}

const searchFiltersTracking = () => {
    getFilters();
};

export default searchFiltersTracking;