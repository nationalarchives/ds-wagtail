export default function () {
    let $parentForm = document.querySelector('[data-id="long-filter-form"]');

    let $longFiltersContainer = document.querySelector('[data-id="long-filters-container"]');

    let $longFiltersList = document.querySelector('[data-id="long-filters-list"]');
    let $longFiltersListItems = document.querySelectorAll('[data-class="long-filters-list-item"]');

    if(!$longFiltersContainer || !$longFiltersListItems || !$longFiltersList) {
        return;
    }

    let longFiltersArray = [...$longFiltersListItems];

    let $searchDiv = document.createElement('div');
    $searchDiv.setAttribute('class', 'long-filters__search');
    let $searchBox = document.createElement('input');
    $searchBox.setAttribute('class', 'long-filters__search-box');
    let searchId = 'long-filters-search-box';
    $searchBox.id = searchId;
    let $searchLabel = document.createElement('label');
    $searchLabel.innerText = "Narrow down filters";
    $searchLabel.setAttribute('for', searchId);
    $searchLabel.setAttribute('class', 'long-filters__search-label');

    let $searchButton = document.createElement('button');
    $searchButton.innerText = 'Search';
    $searchButton.setAttribute('class', 'long-filters__search-button');

    $searchDiv.appendChild($searchLabel);
    $searchDiv.appendChild($searchBox);
    $searchDiv.appendChild($searchButton);


    $longFiltersContainer.insertBefore($searchDiv, $longFiltersContainer.childNodes[0]);


    let handleSearch = function(e) {
        e.preventDefault();
        let keyword = $searchBox.value.toLowerCase();

        let narrowedDownFilters = longFiltersArray.filter(filter => {
            let filterLabel = filter.childNodes[0];
            let filterInput = filterLabel.childNodes[0];

            // Keep the filter if it matches the users keyword, or if the filter is selected.
            return filter.innerText.toLowerCase().includes(keyword) || filterInput.checked;
        });

        $longFiltersList.replaceChildren(...narrowedDownFilters);
    }

    let disableSearchSubmit = function(e) {
        if(e.key === "Enter") {
            handleSearch(e);
        }
    }

    $searchButton.addEventListener('click', handleSearch);
    $searchBox.addEventListener('keyup', handleSearch);
    $parentForm.addEventListener('keypress', disableSearchSubmit)

}