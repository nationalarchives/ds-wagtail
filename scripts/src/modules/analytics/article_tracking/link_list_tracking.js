export default function link_list_tracking() {
    if (document.querySelector(".related-resources")) {
        const link_list_grandparent =
            document.querySelector(".related-resources").parentElement
                .parentElement;
        const link_list_links = document.querySelectorAll(
            ".related-resources__link"
        );
        const section_name = link_list_grandparent
            .querySelector(`h2`)
            .textContent.trim();

        Array.prototype.forEach.call(link_list_links, (item, index) => {
            const component_name = item.getAttribute("data-component-name");
            item.setAttribute(
                "data-component-name",
                component_name + section_name
            );
            item.setAttribute("data-position", index);
        });
    }
}
