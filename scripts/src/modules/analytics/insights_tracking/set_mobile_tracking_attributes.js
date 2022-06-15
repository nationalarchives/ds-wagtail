export default function set_mobile_tracking_attributes(section_headings) {
    Array.prototype.forEach.call(section_headings, (item, index) => {
        const isExpanded = item.getAttribute("aria-expanded") === "true" ? true : false;

        item.setAttribute("data_component_name", "Mobile in page navigation");
        item.setAttribute("data_link_type", `${isExpanded ? "Expand" : "Collapse"} header no. ${index + 1}`);
        item.setAttribute("data_link", item.textContent.trim());
    });
}
