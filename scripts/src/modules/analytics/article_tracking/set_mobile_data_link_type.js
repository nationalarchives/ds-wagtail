export default function toggle_data_link_type(e) {
    const isExpanded =
        e.target.getAttribute("aria-expanded") === "true" ? true : false;

    e.target.setAttribute(
        "data-link-type",
        `${isExpanded ? "Expand" : "Collapse"} accordion`
    );

    return e.target.getAttribute("data-link-type");
}
