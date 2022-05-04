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
    let $searchBox = document.createElement('input');
    let searchId = 'long-filters-search-box';
    $searchBox.id = searchId;
    let $searchLabel = document.createElement('label');
    $searchLabel.innerText = "Find filters by keyword";
    $searchLabel.setAttribute('for', searchId);
    let $searchButton = document.createElement('button');
    $searchButton.innerText = 'Search all filters';

    $searchDiv.appendChild($searchLabel);
    $searchDiv.appendChild($searchBox);
    $searchDiv.appendChild($searchButton);


    $longFiltersContainer.insertBefore($searchDiv, $longFiltersContainer.childNodes[0]);


    let handleSearch = function(e) {
        e.preventDefault();
        let keyword = $searchBox.value.toLowerCase();

        let narrowedDownFilters = longFiltersArray.filter(filter => {
            return filter.innerText.toLowerCase().includes(keyword);
        });

        $longFiltersList.replaceChildren(...narrowedDownFilters);
    }

    let disableSearchSubmit = function(e) {
        if(e.key === "Enter") {
            handleSearch(e);
        }
    }

    $searchButton.addEventListener('click', handleSearch);
    $parentForm.addEventListener('keypress', disableSearchSubmit)

}