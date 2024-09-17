/* global $buttonHtml $noOfFilters */
import debounce from "../debounce.js";

export default function () {
    let $searchGrid = document.querySelector(
        'div[data-id="catalogue-search-grid"]',
    );
    let $searchFilterContainer = document.querySelector(
        'div[data-id="catalogue-search-sidebar"]',
    );

    let $main = document.querySelector("main");

    if (!$searchFilterContainer || !$searchGrid || !$main) {
        return;
    }

    //need case where validation warning is invoked
    let $showHideButton = document.createElement("button");
    //check the query string to populate the number of selected filters
    if (window.location.href.indexOf("filter_keyword") != -1) {
        $showHideButton.innerHTML = $buttonHtml;
    } else {
        // no filters selected (always display number of active filters)
        $showHideButton.innerHTML =
            "Add filters" +
            '<span class="sr-only"> active</span><img src="/static/images/fontawesome-svgs/chevron-down-white.svg" width="20" height="20" style="display:inline-block;margin-left:10px;">';
    }
    $showHideButton.classList.add("search-results__filter-button");
    $showHideButton.setAttribute("aria-expanded", false);
    $showHideButton.setAttribute("aria-controls", "searchFilterContainer");
    $showHideButton.setAttribute("data-link-type", "Mobile Button");
    $showHideButton.setAttribute("data-link", "Show search filters");
    $showHideButton.hidden = true;

    //console.log($showHideButton);
    //console.log($searchGrid);

    //$main.insertBefore($showHideButton, $searchGrid);
    $searchGrid.after($showHideButton, $searchGrid);

    $searchFilterContainer.id = "searchFilterContainer";

    $showHideButton.addEventListener("click", function (e) {
        e.preventDefault();
        let ariaExpanded =
            $showHideButton.getAttribute("aria-expanded") == "true";
        $showHideButton.setAttribute("aria-expanded", !ariaExpanded);
        let newAriaExpanded =
            $showHideButton.getAttribute("aria-expanded") == "true";
        $searchFilterContainer.hidden = !$searchFilterContainer.hidden;

        if (newAriaExpanded) {
            $showHideButton.innerHTML =
                'Hide filters <img src="/static/images/fontawesome-svgs/chevron-up-white.svg" width="20px" height="20px" style=\'display: inline-block;margin-left: 10px;\'>';
        } else {
            $showHideButton.innerHTML =
                'Add filters<span class="filter-indicator">' +
                $noOfFilters +
                '<span class="sr-only"> active</span></span><img src="/static/images/fontawesome-svgs/chevron-down-white.svg" width="20" height="20" style=\'display: inline-block;margin-left: 10px;\'>';
        }
    });

    if (window.innerWidth <= 992) {
        $showHideButton.hidden = false;
        $searchFilterContainer.hidden = true;
    }

    window.addEventListener(
        "resize",
        debounce(() => {
            let ariaExpanded = $showHideButton.getAttribute("aria-expanded");

            if (window.innerWidth <= 992) {
                $showHideButton.hidden = false;

                if (ariaExpanded === "false") {
                    $searchFilterContainer.hidden = true;
                } else {
                    $searchFilterContainer.hidden = false;
                }
            } else {
                $showHideButton.hidden = true;
                $searchFilterContainer.hidden = false;
            }
        }, 200),
    );
}
