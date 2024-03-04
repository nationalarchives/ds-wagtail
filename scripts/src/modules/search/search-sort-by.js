export default function () {
    const sortByForm = document.querySelector("[data-sort-search]");
    const sortBySelector = sortByForm.querySelector("#id_sort_by_desktop");

    if (!sortByForm || !sortBySelector) {
        return;
    } else {
        sortBySelector.addEventListener("change", function () {
            sortByForm.submit();
        });
    }
}
