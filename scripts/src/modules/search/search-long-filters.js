export default function () {
    const $parentForm = document.querySelector('[data-id="long-filter-form"]');

    const $longFiltersContainer = document.querySelector('[data-id="long-filters-container"]');

    const $longFiltersList = document.querySelector('[data-id="long-filters-list"]');
    const $longFiltersListItems = document.querySelectorAll('[data-class="long-filters-list-item"]');

    if(!$longFiltersContainer || !$longFiltersListItems || !$longFiltersList) {
        return;
    }

    const longFiltersArray = [].slice.call($longFiltersListItems); // IE11 equivalent of doing [...$longFiltersListItems]

    const $searchDiv = document.createElement('div');
    $searchDiv.setAttribute('class', 'long-filters__search');
    const $searchBox = document.createElement('input');
    $searchBox.setAttribute('class', 'long-filters__search-box');
    const searchId = 'long-filters-search-box';
    $searchBox.id = searchId;
    const $searchLabel = document.createElement('label');
    $searchLabel.innerText = "Narrow down filters";
    $searchLabel.setAttribute('for', searchId);
    $searchLabel.setAttribute('class', 'long-filters__search-label');

    const $searchButton = document.createElement('button');
    $searchButton.innerText = 'Search';
    $searchButton.setAttribute('class', 'long-filters__search-button');

    $searchDiv.appendChild($searchLabel);
    $searchDiv.appendChild($searchBox);
    $searchDiv.appendChild($searchButton);


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

    }

    const disableSearchSubmit = function(e) {
        if(e.key === "Enter") {
            handleSearch(e);
        }
    }

    $searchButton.addEventListener('click', handleSearch);
    $searchBox.addEventListener('keyup', handleSearch);
    $parentForm.addEventListener('keypress', disableSearchSubmit)

}