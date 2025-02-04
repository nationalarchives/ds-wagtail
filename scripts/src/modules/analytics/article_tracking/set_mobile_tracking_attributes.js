export default function set_mobile_tracking_attributes(section_headings) {
    Array.prototype.forEach.call(section_headings, (item, index) => {
        const isExpanded =
            item.getAttribute("aria-expanded") === "true" ? true : false;

        item.setAttribute("data-component-name", "Mobile in page navigation");
        item.setAttribute(
            "data-link-type",
            `${isExpanded ? "Expand" : "Collapse"} accordion`,
        );
        item.setAttribute("data-position", index);
        item.setAttribute("data-link", item.textContent.trim());
    });
}
