import push_to_data_layer from "./../push_to_data_layer";

const getSortBy = () => {
    // get filters after DOM has loaded and they have rendered on page
    window.addEventListener("load", () => {
        var selectElementDesktop = document.querySelector(
            "#id_sort_by_desktop",
        );
        var selectElementMobile = document.querySelector("#id_sort_by_mobile");

        if (selectElementDesktop) {
            const selectOutputDesktop =
                selectElementDesktop.options[
                    selectElementDesktop.selectedIndex
                ].value.trim();
            var sortByDesktop = selectElementDesktop.parentElement;
            sortByDesktop.setAttribute(
                "data-search-filter-value",
                selectOutputDesktop,
            );

            selectElementDesktop.onchange = function () {
                let selectOutputDesktop =
                    this.options[this.selectedIndex].value.trim();
                if (selectOutputDesktop == "") {
                    selectOutputDesktop = "relevance";
                }
                sortByDesktop.setAttribute(
                    "data-search-filter-value",
                    selectOutputDesktop,
                );
            };

            const searchTypeDesktop =
                sortByDesktop.getAttribute("data-search-type");
            const searchBucketDesktop =
                sortByDesktop.getAttribute("data-search-bucket");

            sortByDesktop.addEventListener("submit", (e) => {
                e.preventDefault();

                let searchNameDesktop = sortByDesktop.getAttribute(
                    "data-search-filter-name",
                );
                let searchValueDesktop = sortByDesktop.getAttribute(
                    "data-search-filter-value",
                );

                let filterDataDesktop = {
                    event: "sort-results",
                    search_type: searchTypeDesktop || "",
                    search_bucket: searchBucketDesktop || "",
                    search_filter_name: searchNameDesktop || "",
                    search_filter_value: searchValueDesktop || "relevance",
                };

                push_to_data_layer(filterDataDesktop);

                sortByDesktop.submit();
            });
        }

        if (selectElementMobile) {
            const selectOutputMobile =
                selectElementMobile.options[
                    selectElementMobile.selectedIndex
                ].value.trim();
            var sortByMobile = selectElementMobile.parentElement;
            sortByMobile.setAttribute(
                "data-search-filter-value",
                selectOutputMobile,
            );

            selectElementMobile.onchange = function () {
                let selectOutputMobile =
                    this.options[this.selectedIndex].value.trim();
                if (selectOutputMobile == "") {
                    selectOutputMobile = "relevance";
                }
                sortByMobile.setAttribute(
                    "data-search-filter-value",
                    selectOutputMobile,
                );
            };

            const searchTypeMobile =
                sortByMobile.getAttribute("data-search-type");
            const searchBucketMobile =
                sortByMobile.getAttribute("data-search-bucket");

            sortByMobile.addEventListener("submit", (e) => {
                e.preventDefault();

                let searchNameMobile = sortByMobile.getAttribute(
                    "data-search-filter-name",
                );
                let searchValueMobile = sortByMobile.getAttribute(
                    "data-search-filter-value",
                );

                let filterDataMobile = {
                    event: "sort-results",
                    search_type: searchTypeMobile || "",
                    search_bucket: searchBucketMobile || "",
                    search_filter_name: searchNameMobile || "",
                    search_filter_value: searchValueMobile || "relevance",
                };

                push_to_data_layer(filterDataMobile);

                sortByMobile.submit();
            });
        }
    });
};

const searchSortFiltersTracking = () => {
    getSortBy();
};

export default searchSortFiltersTracking;
