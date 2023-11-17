import FiltersSubmission from "./modules/filters-submission";
import Accordion from "./modules/accordion";

document.addEventListener("DOMContentLoaded", () => {
    for (const filtersSubmission of document.querySelectorAll(
        "[data-js-filters-submission]",
    )) {
        new FiltersSubmission(filtersSubmission);
    }

    for (const accordion of document.querySelectorAll("[data-accordion]")) {
        new Accordion(accordion);
    }
});
