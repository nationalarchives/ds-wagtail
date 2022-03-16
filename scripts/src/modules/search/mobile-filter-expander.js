import debounce from '../debounce.js';

export default function() {
    let $searchGrid = document.querySelector('div[data-id="catalogue-search-grid"]');
    let $searchFilterContainer = document.querySelector('div[data-id="catalogue-search-sidebar"]');
    let $searchForm = document.querySelector('form[data-id="search-form"]');

    if(!$searchFilterContainer || !$searchGrid || !$searchForm) {
        return;
    }

    let $showHideButton = document.createElement('button');
    $showHideButton.innerText = 'Show search filters';
    $showHideButton.classList.add('search-results__filter-button');
    $showHideButton.setAttribute('aria-expanded', false);
    $showHideButton.setAttribute('aria-controls', 'searchFilterContainer');
    $showHideButton.setAttribute('aria-label', 'Show or hide filters');
    $showHideButton.hidden = true;
    $searchForm.insertBefore($showHideButton, $searchGrid);

    $searchFilterContainer.id = 'searchFilterContainer';

    $showHideButton.addEventListener('click', function(e) {
        e.preventDefault();
        let ariaExpanded = $showHideButton.getAttribute('aria-expanded') == 'true';
        $showHideButton.setAttribute('aria-expanded', !ariaExpanded);
        let newAriaExpanded = $showHideButton.getAttribute('aria-expanded') == 'true';
        $searchFilterContainer.hidden = !$searchFilterContainer.hidden;

        if(newAriaExpanded) {
            $showHideButton.innerHTML = 'Hide search filters';
        }
        else {
            $showHideButton.innerHTML = 'Show search filters';
        }
    });

    if(window.innerWidth <= 1200) {
        $showHideButton.hidden = false;
        $searchFilterContainer.hidden = true;
    }

    window.addEventListener("resize", debounce(() =>{
        let ariaExpanded = $showHideButton.getAttribute('aria-expanded');
        if(window.innerWidth <= 1200) {
            $showHideButton.hidden = false;

            if(ariaExpanded === 'false') {
                $searchFilterContainer.hidden = true;
            }
            else {
                $searchFilterContainer.hidden = false;
            }
        }
        else {
            $showHideButton.hidden = true;
            $searchFilterContainer.hidden = false;
        }
    }, 200));
};
