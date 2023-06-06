export default function () {
    let $toggleLink = document.querySelector(
        'div[data-id="hierarchy-toggle-link"]'
    );
    let $detailedView = document.querySelector(
        'nav[data-id="hierarchy-detailed-view"]'
    );

    if (!$toggleLink || !$detailedView) {
        return;
    }

    let $showHideButton = document.createElement("button");
    $showHideButton.innerText = "Show detailed view";
    $showHideButton.classList.add("hierarchy-short-panel__toggle-button");
    $showHideButton.setAttribute("aria-expanded", false);
    $showHideButton.setAttribute("aria-controls", "hierarchy-togglee");
    $showHideButton.setAttribute("aria-label", "Show or hide detailed view");
    $showHideButton.setAttribute("data-link-type", "Expand accordion");
    $showHideButton.setAttribute("data-link", "Show detailed view");
    $showHideButton.setAttribute("data-component-name", "Catalogue hierarchy");
    $toggleLink.appendChild($showHideButton);

    $detailedView.id = "hierarchyTogglee";
    $detailedView.hidden = true;

    $showHideButton.addEventListener("click", function (e) {
        e.preventDefault();
        let ariaExpanded =
            $showHideButton.getAttribute("aria-expanded") == "true";
        $showHideButton.setAttribute("aria-expanded", !ariaExpanded);
        let newAriaExpanded =
            $showHideButton.getAttribute("aria-expanded") == "true";
        $detailedView.hidden = !$detailedView.hidden;

        if (newAriaExpanded) {
            $showHideButton.innerHTML = "Hide detailed view";
            $showHideButton.setAttribute("class", "open");
            $showHideButton.setAttribute(
                "data-link-type",
                "Collapse accordion"
            );
            $showHideButton.setAttribute("data-link", "Hide detailed view");
        } else {
            $showHideButton.innerHTML = "Show detailed view";
            $showHideButton.setAttribute("class", "");
            $showHideButton.setAttribute("data-link-type", "Expand accordion");
            $showHideButton.setAttribute("data-link", "Show detailed view");
        }
    });
}
