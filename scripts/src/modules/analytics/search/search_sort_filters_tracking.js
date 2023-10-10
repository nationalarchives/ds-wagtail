import push_to_data_layer from "./../push_to_data_layer";

const getSortBy = () => {
    // get filters after DOM has loaded and they have rendered on page
    window.addEventListener("load", () => {
        var desktop = true;
        var selectElement = document.querySelector("#id_sort_by_desktop");
        if (selectElement.checkVisibility() == false) {
            desktop = false;
            selectElement = document.querySelector("#id_sort_by_mobile");
        }

        // check if selectElement exists to avoid errors on other search pages
        if (selectElement) {
            const selectOutput =
                selectElement.options[selectElement.selectedIndex].value.trim();
            if (desktop) {
                var sortBy = document.querySelector('[data-id="sort-form-desktop"]');
            } else {
                var sortBy = document.querySelector('[data-id="sort-form-mobile"]');
            }
            sortBy.setAttribute("data-search-filter-value", selectOutput);
            selectElement.onchange = function () {
                let selectOutput =
                    this.options[this.selectedIndex].value.trim();
                if (selectOutput == "") {
                    selectOutput = "relevance";
                }
                sortBy.setAttribute("data-search-filter-value", selectOutput);
            };

            const searchType = sortBy.getAttribute("data-search-type");
            const searchBucket = sortBy.getAttribute("data-search-bucket");

            sortBy.addEventListener("submit", (e) => {
                e.preventDefault();

                let searchName = sortBy.getAttribute("data-search-filter-name");
                let searchValue = sortBy.getAttribute(
                    "data-search-filter-value",
                );

                let filterData = {
                    event: "sort-results",
                    search_type: searchType || "",
                    search_bucket: searchBucket || "",
                    search_filter_name: searchName || "",
                    search_filter_value: searchValue || "relevance",
                };

                push_to_data_layer(filterData);

                sortBy.submit();
            });
        }
    });
};

const searchSortFiltersTracking = () => {
    getSortBy();
};

export default searchSortFiltersTracking;
