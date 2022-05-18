export default function () {
    const $parentForm = document.querySelector('[data-id="long-filter-form"]');

    const $longFiltersContainer = document.querySelector('[data-id="long-filters-container"]');

    const $longFiltersList = document.querySelector('[data-id="long-filters-list"]');
    const $longFiltersListItems = document.querySelectorAll('[data-class="long-filters-list-item"]');

    const $longFiltersLegend = document.querySelector('[data-id="long-filters-legend"]');
    const $longFiltersFieldset = document.querySelector('[data-id="long-filters-fieldset"]');

    if(!$parentForm || !$longFiltersContainer || !$longFiltersListItems || !$longFiltersList || !$longFiltersLegend || !$longFiltersFieldset) {
        return;
    }

    const longFiltersArray = [].slice.call($longFiltersListItems); // IE11 equivalent of doing [...$longFiltersListItems]

    const $searchDiv = document.createElement('div');
    $searchDiv.setAttribute('class', 'long-filters__search');
    const $searchBox = document.createElement('input');
    $searchBox.setAttribute('class', 'long-filters__search-box');
    $searchBox.setAttribute('type', 'search');
    const searchId = 'long-filters-search-box';
    $searchBox.id = searchId;
    const $searchLabel = document.createElement('label');
    $searchLabel.innerText = "Narrow down filters";
    $searchLabel.setAttribute('for', searchId);
    $searchLabel.setAttribute('class', 'long-filters__search-label');

    let $searchHelperText = document.createElement('p');
    $searchHelperText.innerText = 'Filters that contain the text you enter will be displayed. Filters you have checked will always be shown.';
    $searchHelperText.id = 'long-filters-helper-text';
    $searchBox.setAttribute('aria-describedby', 'long-filters-helper-text');

    $searchDiv.appendChild($searchLabel);
    $searchDiv.appendChild($searchBox);
    $searchDiv.appendChild($searchHelperText);

    const $filterCount = document.createElement('p');
    $filterCount.id = 'long-filters-count';
    $filterCount.setAttribute('class', 'long-filters__count');
    $longFiltersFieldset.setAttribute('aria-describedby', 'long-filters-count');

    const totalFiltersLength = longFiltersArray.length;
    let longFiltersCountText = `Showing ${totalFiltersLength} out of ${totalFiltersLength} filters`;
    $filterCount.innerText = longFiltersCountText;

    $longFiltersFieldset.insertBefore($filterCount, $longFiltersFieldset.childNodes[2]);

    $longFiltersContainer.insertBefore($searchDiv, $longFiltersContainer.childNodes[0]);

    const handleSearch = function(e) {
        e.preventDefault();
        const keyword = $searchBox.value.toLowerCase();

        const narrowedDownFilters = longFiltersArray.filter(filter => {

            if(filter.childNodes.length === 0) {
                return false;
            }

            const filterLabel = filter.childNodes[0];
            const filterInput = filterLabel.childNodes[0];

            // Keep the filter if it matches the users keyword, or if the filter is selected.
            return filterLabel.innerText.toLowerCase().indexOf(keyword) != -1 || filterInput.checked;
        });

        /* IE11 compatible method to remove children without affecting the JS APIs. 
           Using $longFiltersList.innerHTML = ''; causes issues on IE11.
        */
        while ($longFiltersList.firstChild) {
            $longFiltersList.removeChild($longFiltersList.firstChild);
        }

        for(const filter of narrowedDownFilters) {
            $longFiltersList.appendChild(filter);
        }

        let narrowedFiltersLength = narrowedDownFilters.length;
        longFiltersCountText = `Showing ${narrowedFiltersLength} out of ${totalFiltersLength} filters`;
        $filterCount.innerText = longFiltersCountText;

    }

    // Prevents the whole form from submitting when pressing "Enter" on search filter box
    const disableSearchSubmit = function(e) {
        if(e.key === "Enter" && e.target.id === $searchBox.id) {
            handleSearch(e);
        }
    }

    $searchBox.addEventListener('keyup', handleSearch);
    $parentForm.addEventListener('keypress', disableSearchSubmit)

}