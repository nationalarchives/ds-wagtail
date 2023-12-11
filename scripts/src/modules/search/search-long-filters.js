export default function () {
    const $parentForm = document.querySelector('[data-id="long-filter-form"]');

    const $longFiltersSearchContainer = document.querySelector(
        '[data-id="long-filters-search-container"]',
    );

    const $longFiltersList = document.querySelector(
        '[data-id="long-filters-list"]',
    );
    const $longFiltersListItems = document.querySelectorAll(
        '[data-class="long-filters-list-item"]',
    );

    const $longFiltersLegend = document.querySelector(
        '[data-id="long-filters-legend"]',
    );
    const $longFiltersFieldset = document.querySelector(
        '[data-id="long-filters-fieldset"]',
    );

    if (
        !$parentForm ||
        !$longFiltersSearchContainer ||
        !$longFiltersListItems ||
        !$longFiltersList ||
        !$longFiltersLegend ||
        !$longFiltersFieldset
    ) {
        return;
    }

    const longFiltersArray = [].slice.call($longFiltersListItems); // IE11 equivalent of doing [...$longFiltersListItems]

    const $searchDiv = document.createElement("div");
    $searchDiv.setAttribute("class", "long-filters__search");
    const $searchBox = document.createElement("input");
    $searchBox.setAttribute("class", "long-filters__search-box");
    $searchBox.setAttribute("type", "search");
    const searchId = "long-filters-search-box";
    $searchBox.id = searchId;
    const $searchLabel = document.createElement("label");
    $searchLabel.innerText = "Narrow down filters";
    $searchLabel.setAttribute("for", searchId);
    $searchLabel.setAttribute("class", "long-filters__search-label");

    let $searchHelperText = document.createElement("p");
    $searchHelperText.innerText =
        "Enter text to refine your filters. Already selected filters will remain active.";
    $searchHelperText.setAttribute("class", "long-filters__helper-text");
    $searchHelperText.id = "long-filters-helper-text";
    $searchBox.setAttribute("aria-describedby", "long-filters-helper-text");

    $searchDiv.appendChild($searchLabel);
    $searchDiv.appendChild($searchBox);
    $searchDiv.appendChild($searchHelperText);

    const $filterCount = document.createElement("p");
    $filterCount.id = "long-filters-count";
    $filterCount.setAttribute("class", "long-filters__count");
    $longFiltersFieldset.setAttribute("aria-describedby", "long-filters-count");

    const totalFiltersLength = longFiltersArray.length;
    let longFiltersCountText = `Showing ${totalFiltersLength} of ${totalFiltersLength} filters`;
    $filterCount.innerText = longFiltersCountText;

    $longFiltersFieldset.insertBefore(
        $filterCount,
        $longFiltersFieldset.childNodes[2],
    );

    $longFiltersSearchContainer.insertBefore(
        $searchDiv,
        $longFiltersSearchContainer.childNodes[0],
    );

    //create a const for the intro paragraph for collections
    const $introCopy = document.createElement("p");
    $introCopy.setAttribute("class", "long-filters__intro");
    $introCopy.innerText =
        "Filter by collections of records, which are typically organised by government department and consist of many items.";

    //create a const for the intro paragraph for Held by
    const $introCopyheldby = document.createElement("p");
    $introCopyheldby.setAttribute("class", "long-filters__intro");
    $introCopyheldby.innerText =
        "Filter by holding archives and other organisations, for example local archives or record offices.";

    //check to see if it is 'collections' results or 'held by' results that is being searched for.
    if (window.location.href.indexOf("collection") != -1) {
        // console.log('collections');
        //append intro paragraph
        $filterCount.appendChild($introCopy);
    }
    if (window.location.href.indexOf("held_by") != -1) {
        //console.log('held by');
        $filterCount.appendChild($introCopyheldby);
    }

    const handleSearch = function () {
        const keyword = $searchBox.value.toLowerCase();

        const narrowedDownFilters = longFiltersArray.filter((filter) => {
            if (filter.childNodes.length === 0) {
                return false;
            }

            const filterLabel = filter.childNodes[0];
            const filterInput = filterLabel.childNodes[0];

            // Keep the filter if it matches the users keyword, or if the filter is selected.
            return (
                filterLabel.innerText.toLowerCase().indexOf(keyword) != -1 ||
                filterInput.checked
            );
        });

        /* IE11 compatible method to remove children without affecting the JS APIs.
           Using $longFiltersList.innerHTML = ''; causes issues on IE11.
        */
        while ($longFiltersList.firstChild) {
            $longFiltersList.removeChild($longFiltersList.firstChild);
        }

        for (const filter of narrowedDownFilters) {
            $longFiltersList.appendChild(filter);
        }

        let narrowedFiltersLength = narrowedDownFilters.length;
        longFiltersCountText = `Showing ${narrowedFiltersLength} out of ${totalFiltersLength} filters`;
        $filterCount.innerText = longFiltersCountText;
    };

    // Prevents the whole form from submitting when pressing "Enter" on search filter box
    const disableSearchSubmit = function (e) {
        if (e.key === "Enter" && e.target.id === $searchBox.id) {
            e.preventDefault();
        }
    };

    $searchBox.addEventListener("keyup", handleSearch);
    $parentForm.addEventListener("keypress", disableSearchSubmit);
}
