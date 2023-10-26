import FiltersSubmission from "./modules/filters-submission";

document.addEventListener("DOMContentLoaded", () => {
    for (const filtersSubmission of document.querySelectorAll(
        "[data-js-filters-submission]",
    )) {
        new FiltersSubmission(filtersSubmission);
    }
});
