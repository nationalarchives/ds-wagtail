import push_to_data_layer from "../push_to_data_layer";

const longFiltersTracking = () => {
    // get filters after DOM has loaded and they have rendered on page
    window.addEventListener("load", () => {
        const longFilters = document.querySelector("[data-long-filters]");

        if (longFilters) {
            const longFiltersList = longFilters.querySelector(
                "[data-long-filters-list]",
            );
            const longFilterItems = longFiltersList.querySelectorAll(
                "[data-long-filters-item] input",
            );
            // create array to store checked filters
            const checkedLongFilters = [];
            const activeLongFilters = [];

            // listen for checkboxes and store in array
            longFilterItems.forEach((filter) => {
                filter.addEventListener("change", function () {
                    checkedLongFilters.push(filter);
                });
            });

            longFilters.addEventListener("submit", (e) => {
                e.preventDefault();

                checkedLongFilters.forEach((filter) => {
                    let filterName = filter.name;
                    let filterValue = filter.value;

                    let filterData = {
                        event: "search-long-filter",
                        "search-filter-name": filterName || "",
                        "search-filter-value": filterValue || "",
                    };

                    // add checked filters to activeFilters array
                    activeLongFilters.push(filterData);
                });

                // loop through the updated filters array and send each item to the dataLayer
                activeLongFilters.forEach((filter) => {
                    push_to_data_layer(filter);
                });

                longFilters.submit();
            });
        }
    });
};

export default longFiltersTracking;
