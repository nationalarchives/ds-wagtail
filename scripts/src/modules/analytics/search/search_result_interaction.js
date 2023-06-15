import push_to_data_layer from "./../push_to_data_layer";

const addPositionToSearchResults = () => {
    const results = document.querySelectorAll('[data-analytics-link]');

    Array.prototype.forEach.call(results, (element, index) => {
        element.dataset.analyticsPosition = index;
    })
};

const addListenersToResultsList = () => {
    const resultsList = document.getElementById('analytics-results-list');

    const bucket = document.getElementById('analytics-current-bucket')?.dataset?.currentBucket;

    // check if resultsList exists to avoid errors on other search pages
    if (resultsList) {
        resultsList.addEventListener('click', (event) => {
            if (event.target.classList.contains("search-results__list-card-link")) {
    
                const eventData = {
                    'event': 'search-result' || '',
                    'search-bucket': bucket || '',
                    'data-link-type': 'Search results list' || '',
                    'data-link': event.target.dataset.analyticsLink || '',
                    'data-position': event.target.dataset.analyticsPosition || '',
                };
    
                push_to_data_layer(eventData);
            }
        });
    }

    
};

const intialiseSearchResultTracking = () => {
    addPositionToSearchResults();
    addListenersToResultsList();
};

export default intialiseSearchResultTracking;
