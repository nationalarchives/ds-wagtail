import debounce from "../debounce.js";

export default function () {
    let $searchBuckets = document.querySelector(".search-buckets");

    if (!$searchBuckets) {
        return;
    }

    let $searchBucketsToHide = document.querySelectorAll(
        "ul[data-id=search-buckets-list] li:not([data-current=true])"
    );

    let $showHideButton = document.createElement("button");
    $showHideButton.innerText = "Show more result categories";
    $showHideButton.classList.add("search-buckets__toggle-button");
    $showHideButton.setAttribute("aria-expanded", false);
    $showHideButton.setAttribute(
        "aria-label",
        "Show or hide result categories"
    );
    $showHideButton.setAttribute("data-link-type", "Link");
    $showHideButton.setAttribute("data-link", "Show more result categories");
    $showHideButton.hidden = true;
    $searchBuckets.insertBefore($showHideButton, $searchBuckets.childNodes[0]); //IE11 compatible prepend

    let ariaControls = "";
    for (let i = 0; i < $searchBucketsToHide.length; i++) {
        let $bucket = $searchBucketsToHide[i];
        let id = `bucket-${i}`;
        $bucket.id = id; // Needed for aria-controls
        ariaControls = `${ariaControls}${id} `;
    }

    $showHideButton.setAttribute("aria-controls", ariaControls);

    $showHideButton.addEventListener("click", function (e) {
        e.preventDefault();
        let ariaExpanded =
            $showHideButton.getAttribute("aria-expanded") == "true";
        $showHideButton.setAttribute("aria-expanded", !ariaExpanded);
        let newAriaExpanded =
            $showHideButton.getAttribute("aria-expanded") == "true";

        for (let i = 0; i < $searchBucketsToHide.length; i++) {
            let $bucket = $searchBucketsToHide[i];
            $bucket.hidden = !$bucket.hidden;
        }

        if (newAriaExpanded) {
            $showHideButton.innerHTML = "Hide more result categories";
        } else {
            $showHideButton.innerHTML = "Show more result categories";
        }
    });

    if (window.innerWidth <= 768) {
        $showHideButton.hidden = false;
        for (let i = 0; i < $searchBucketsToHide.length; i++) {
            let $bucket = $searchBucketsToHide[i];
            $bucket.hidden = true;
        }
    }

    window.addEventListener(
        "resize",
        debounce(() => {
            let ariaExpanded = $showHideButton.getAttribute("aria-expanded");
            if (window.innerWidth <= 768) {
                $showHideButton.hidden = false;

                if (ariaExpanded === "false") {
                    for (let i = 0; i < $searchBucketsToHide.length; i++) {
                        let $bucket = $searchBucketsToHide[i];
                        $bucket.hidden = true;
                    }
                }
            } else {
                $showHideButton.hidden = true;
                $showHideButton.setAttribute("aria-expanded", false);
                $showHideButton.innerHTML = "Show more result categories";

                for (let i = 0; i < $searchBucketsToHide.length; i++) {
                    let $bucket = $searchBucketsToHide[i];
                    $bucket.hidden = false;
                }
            }
        }, 200)
    );
}
