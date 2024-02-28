export default function () {
    const sortByForm = document.querySelector("[data-sort-search]");
    const sortBySelector = sortByForm.querySelector("#id_sort_by_desktop");

    sortBySelector.addEventListener("change", function () {
        console.log("clicked select");
        sortByForm.submit();
    });
}
