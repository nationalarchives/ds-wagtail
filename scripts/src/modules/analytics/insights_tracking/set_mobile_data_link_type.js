export default function toggle_data_link_type(e, section_headings) {
    const isExpanded = e.target.getAttribute("aria-expanded") === "true" ? true : false;

    e.target.setAttribute("data-link-type", `${isExpanded ? "Expand" : "Collapse"} header no. ${Array.prototype.indexOf.call(section_headings, e.target) + 1}`);

    return e.target.getAttribute("data-link-type");
}
