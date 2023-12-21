import push_to_data_layer from "./../push_to_data_layer";

const getSort = () => {
    // get filters after DOM has loaded and they have rendered on page
    window.addEventListener("load", () => {
        var selectElementDesktop = document.querySelector("#id_sort_desktop");
        var selectElementMobile = document.querySelector("#id_sort_mobile");

        if (selectElementDesktop) {
            const selectOutputDesktop =
                selectElementDesktop.options[
                    selectElementDesktop.selectedIndex
                ].value.trim();
            var sortDesktop = selectElementDesktop.parentElement;
            sortDesktop.setAttribute(
                "data-search-filter-value",
                selectOutputDesktop,
            );

            selectElementDesktop.onchange = function () {
                let selectOutputDesktop =
                    this.options[this.selectedIndex].value.trim();
                if (selectOutputDesktop == "") {
                    selectOutputDesktop = "relevance";
                }
                sortDesktop.setAttribute(
                    "data-search-filter-value",
                    selectOutputDesktop,
                );
            };

            const searchTypeDesktop =
                sortDesktop.getAttribute("data-search-type");
            const searchBucketDesktop =
                sortDesktop.getAttribute("data-search-bucket");

            sortDesktop.addEventListener("submit", (e) => {
                e.preventDefault();

                let searchNameDesktop = sortDesktop.getAttribute(
                    "data-search-filter-name",
                );
                let searchValueDesktop = sortDesktop.getAttribute(
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

                sortDesktop.submit();
            });
        }

        if (selectElementMobile) {
            const selectOutputMobile =
                selectElementMobile.options[
                    selectElementMobile.selectedIndex
                ].value.trim();
            var sortMobile = selectElementMobile.parentElement;
            sortMobile.setAttribute(
                "data-search-filter-value",
                selectOutputMobile,
            );

            selectElementMobile.onchange = function () {
                let selectOutputMobile =
                    this.options[this.selectedIndex].value.trim();
                if (selectOutputMobile == "") {
                    selectOutputMobile = "relevance";
                }
                sortMobile.setAttribute(
                    "data-search-filter-value",
                    selectOutputMobile,
                );
            };

            const searchTypeMobile =
                sortMobile.getAttribute("data-search-type");
            const searchBucketMobile =
                sortMobile.getAttribute("data-search-bucket");

            sortMobile.addEventListener("submit", (e) => {
                e.preventDefault();

                let searchNameMobile = sortMobile.getAttribute(
                    "data-search-filter-name",
                );
                let searchValueMobile = sortMobile.getAttribute(
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

                sortMobile.submit();
            });
        }
    });
};

const searchSortFiltersTracking = () => {
    getSort();
};

export default searchSortFiltersTracking;
