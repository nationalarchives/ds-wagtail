export default function () {
    let $toggleLinkCTA = document.querySelector(
        'div[data-id="cta-toggle-link"]'
    );
    let $detailedViewCTA = document.querySelector(
        'div[data-id="cta-detailed-view"]'
    );

    if (!$toggleLinkCTA || !$detailedViewCTA) {
        return;
    }

    let $showHideButton = document.createElement("button");
    $showHideButton.innerText = "Order/download this record";
    $showHideButton.classList.add("cta-primary-panel__link");
    $showHideButton.classList.add("cta-primary-panel__link--primary");
    $showHideButton.setAttribute("aria-expanded", false);
    $showHideButton.setAttribute("aria-controls", "hierarchy-togglee");
    $showHideButton.setAttribute("aria-label", "Order/download this record");
    $showHideButton.setAttribute("data-link-type", "Link");
    $showHideButton.setAttribute("data-link", "Order/download this record");
    $toggleLinkCTA.appendChild($showHideButton);

    $detailedViewCTA.id = "hierarchyTogglee";
    $detailedViewCTA.hidden = true;

    $showHideButton.addEventListener("click", function (e) {
        e.preventDefault();
        let ariaExpanded =
            $showHideButton.getAttribute("aria-expanded") == "true";
        $showHideButton.setAttribute("aria-expanded", !ariaExpanded);
        let newAriaExpanded =
            $showHideButton.getAttribute("aria-expanded") == "true";
        $detailedViewCTA.hidden = !$detailedViewCTA.hidden;

        if (newAriaExpanded) {
            $showHideButton.innerHTML = "Hide order information";
            $showHideButton.setAttribute(
                "class",
                "cta-primary-panel__link cta-primary-panel__link--primary open"
            );
        } else {
            $showHideButton.innerHTML = "Order/download this record";
            $showHideButton.setAttribute(
                "class",
                "cta-primary-panel__link cta-primary-panel__link--primary"
            );
        }
    });
}
