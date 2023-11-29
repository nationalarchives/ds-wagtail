const addPositionToSearchResults = () => {
    const resultsList =
        document.getElementById("analytics-results-list")?.children || [];

    Array.prototype.forEach.call(resultsList, (element, index) => {
        element.querySelector(
            ".search-results__list-card-heading-link",
        ).dataset.position = index;
    });
};

const intialiseSearchResultTracking = () => {
    addPositionToSearchResults();
};

export default intialiseSearchResultTracking;
