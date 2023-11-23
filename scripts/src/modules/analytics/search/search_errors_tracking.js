import push_to_data_layer from "../push_to_data_layer";

const pushActiveErrorsOnLoad = () => {
    // get filters after DOM has loaded and they have rendered on page
    window.addEventListener("load", () => {
        const searchFilters = document.querySelector("[data-search-filters]");

        if (searchFilters) {
            const errors = searchFilters.querySelectorAll(
                "[data-tracking-errors]",
            );
            if (errors !== null) {
                pushActiveErrors(errors);
            }
        }
    });
};

/* eslint-disable no-unused-vars */
const pushActiveErrors = (errors) => {
    const searchFilters = document.querySelector("[data-search-filters]");
    const errorList = searchFilters.querySelectorAll("[data-tracking-errors]");

    // create array to store currently active filters
    const activeErrors = [];

    // loop through all currently active filters
    errorList.forEach((error) => {
        const value = error.getAttribute("data-filter-errors");
        const name = error.getAttribute("data-filter");

        // setup the dataLayer variables for each filter
        let errorData = {
            event: "error-message",
            "search-filter-name": name || "",
            "search-errors": value || "",
        };

        // add currently active filters to activeFilters array
        activeErrors.push(errorData);
    });

    // loop through the updated filters array and send each item to the dataLayer
    activeErrors.forEach((error) => {
        push_to_data_layer(error);
    });
};
/* eslint-enable no-unused-vars */

export default pushActiveErrorsOnLoad;
